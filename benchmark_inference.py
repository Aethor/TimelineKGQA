from typing import Literal, TypedDict, NotRequired, Literal
import os, argparse, re
import ast
import pathlib as pl
import pandas as pd
from collections import defaultdict
from datasets import Dataset
from datasets import load_from_disk, Dataset
from tqdm import tqdm
import dspy
from TimelineKGQA.agentic_retrieval.retrieval import TKGQAQueryTool
from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessage


class ChatMessage(TypedDict):
    role: Literal["user", "assistant", "system", "tool"]
    content: NotRequired[str]
    tool_calls: NotRequired[list]
    name: NotRequired[str]
    reasoning: NotRequired[str | None]
    reasoning_details: NotRequired[str | None]


def get_user_content(messages: list[ChatMessage]) -> str:
    return "\n".join([m["content"] for m in messages if m["role"] == "user"])


def get_reasoning(message: ChatCompletionMessage) -> str | None:
    if hasattr(message, "reasoning"):
        return message.reasoning  # type: ignore
    if hasattr(message, "reasoning_content"):
        return message.reasoning_content  # type: ignore
    if hasattr(message, "reasoning_details"):
        return message.reasoning_details  # type: ignore
    return None


def openai_output_msg_to_input(message: ChatCompletionMessage) -> ChatMessage:
    input_dict: ChatMessage = {"role": "assistant", "content": message.content or ""}
    reasoning = get_reasoning(message)
    if not reasoning is None:
        input_dict["reasoning"] = reasoning
    if not message.tool_calls is None:
        input_dict["tool_calls"] = []
        for tool_call in message.tool_calls:
            if tool_call.type == "function":
                input_dict["tool_calls"].append(
                    {
                        "id": tool_call.id,
                        "function": {
                            "arguments": tool_call.function.arguments,
                            "name": tool_call.function.name,
                        },
                        "type": "function",
                    }
                )
    return input_dict


def openai_output_to_input(response: ChatCompletion) -> list[ChatMessage]:
    return [openai_output_msg_to_input(choice.message) for choice in response.choices]


def batched_inference(
    model_id: str,
    base_url: str,
    api_key: str,
    messages: list[list[ChatMessage]],
    question_info: list[dict],
    max_tokens: int = 16384,
    max_turns: int = 8,
) -> list[list[ChatMessage]]:
    tkgqa_query_tool = TKGQAQueryTool("icewsactor", linking_style="oracle")
    tool_dicts = [tkgqa_query_tool.get_tool_dict()]

    def do_tool_call(name: str, kwargs: dict, events: list[str]) -> str:
        if name == "query_knowledge_base":
            try:
                tool_out = tkgqa_query_tool(
                    kwargs["subject"],
                    kwargs["relation"],
                    kwargs["object"],
                    kwargs["start"],
                    kwargs["end"],
                    # pass in events for oracle linking
                    events=events,
                )
            except Exception as e:
                tool_out = f"error while calling {name}: {e}"
            return tool_out
        else:
            return f"unknown tool: {name}"

    client = OpenAI(base_url=base_url, api_key=api_key)

    completions = []
    print("[warning] inference is sequential, it could be optimized.")
    for msgs, info in tqdm(zip(messages, question_info), total=len(messages)):
        chat_list: list[ChatMessage] = msgs
        tqdm.write(str(msgs))
        turns = 0

        while turns < max_turns:
            try:
                response = client.chat.completions.create(
                    model=model_id,
                    messages=chat_list,
                    tools=tool_dicts,
                    tool_choice="auto",
                    extra_body={"reasoning": {"enabled": True}},
                    max_tokens=max_tokens,
                )
            except Exception as e:
                tqdm.write(str(e))
                break
            tqdm.write(str([choice.message for choice in response.choices]))

            chat_list += openai_output_to_input(response)

            for choice in response.choices:
                if not choice.message.tool_calls:
                    continue
                for tool_call in choice.message.tool_calls:
                    if tool_call.type != "function":
                        continue
                    tool_out = do_tool_call(
                        tool_call.function.name,
                        ast.literal_eval(tool_call.function.arguments),
                        info["events"],
                    )
                    chat_list.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_out,
                            "name": tool_call.function.name,
                        }
                    )
                    tqdm.write(str(chat_list[-1]))

            turns += 1

            got_final_answer = (
                "content" in chat_list[-1]
                and chat_list[-1]["role"] == "assistant"
                and (
                    not "<think>" in chat_list[-1]["content"]
                    or len(parse_model_raw_output([chat_list[-1]]).strip("\n")) > 0
                )
            )

            if got_final_answer:
                break

        completions.append(chat_list)

    return completions


def adjust_system_prompt(example: dict, system_prompt: str) -> dict:
    example["prompt"] = [
        message
        if message["role"] != "system"
        else {"role": "system", "content": system_prompt}
        for message in example["prompt"]
    ]
    return example


def parse_model_raw_output(messages: list[ChatMessage]) -> str:
    thinking_and_output = "\n".join(
        msg["content"]
        for msg in messages
        if "content" in msg and msg["role"] == "assistant"
    )
    if m := re.match(r"<think>.*</think>(.*)", thinking_and_output, re.DOTALL):
        return m.groups()[0].strip()
    # no mark of thinking: return everything
    return thinking_and_output


def get_coarse_answer_type(answer_type: str) -> Literal["temporal", "factual"]:
    if answer_type in {
        "duration",
        "timestamp_end",
        "timestamp_range",
        "timestamp_start",
        "relation_duration",
        "relation_union_or_intersection",
    }:
        return "temporal"
    elif answer_type in {"object", "relation_ranking", "subject"}:
        return "factual"
    else:
        raise ValueError(answer_type)


def is_special_answer_value(answer: str, answer_type: str) -> bool:
    """
    Identify wether an answer is considered a 'special' value for its
    answer type (for example, 'end of time' is a special value for
    'timestamp_start').
    """
    if answer_type in {"timestamp_range", "relation_union_or_intersection"}:
        return "beginning of time" in answer or "end of time" in answer
    elif answer_type == "timestamp_start":
        return answer == "beginning of time"
    elif answer_type == "timestamp_end":
        return answer == "end of time"
    elif answer_type == "duration":
        return answer == "forever"
    elif answer_type == "relation_duration":
        return answer == "There are no intersections between these time intervals."
    elif answer_type in {"subject", "object", "relation_ranking"}:
        return False
    else:
        raise ValueError(answer_type)


def get_coarse_temporal_relation(
    temporal_relation: str,
) -> Literal["timeline", "allen", "union/intersection", "ranking", "duration"]:
    if temporal_relation in {"intersection", "union"}:
        return "union/intersection"
    elif temporal_relation in {"rank_start_time", "rank_end_time"}:
        return "ranking"
    elif temporal_relation == "timeline":
        return "timeline"
    elif temporal_relation in {"average", "sum", "duration_compare"}:
        return "duration"
    # tr like 'duration_1095 days after&duration_finishedby'. it seems
    # that this is *not* in the TKGQA paper. If you watch Figure 2,
    # this type of question is under 'complex', 'factual',
    # 'TPR->TPR->TCO', but is not 'allen' or 'union/intersection'.
    elif temporal_relation.startswith("duration"):
        return "duration"
    elif "X" in temporal_relation and "Y" in temporal_relation:
        return "allen"
    raise ValueError(temporal_relation)


def get_question_type_identifier(row: dict) -> tuple:
    info = row["info"]
    return (
        ("question_level", info["question_level"]),
        ("answer_type", info["answer_type"]),
        ("question_type", info["question_type"]),
        ("temporal_relation", get_coarse_temporal_relation(info["temporal_relation"])),
    )


def load_test_dataset(
    base_dataset_path: str, limit_per_qtype: int, special_limit_proportion: float = 0.1
) -> Dataset:
    """Load a test dataset, filtering examples with certain
    constraints.

    :param base_dataset_path: path to the dataset to load from.
    :param limit_per_qtype: maximum number of examples per question
        type.
    :param special_limit_proportion: maximum proportion of special
        values per question type (see
        :func:`is_special_answer_value`).
    """
    test = load_from_disk(base_dataset_path)["test"]

    type_to_questions = defaultdict(list)
    type_to_special_nb = defaultdict(int)
    for row in test:
        qtype_id = get_question_type_identifier(row)  # type: ignore
        answer_is_special = is_special_answer_value(
            row["answer"], row["info"]["answer_type"]
        )
        if len(type_to_questions[qtype_id]) < limit_per_qtype and (
            not answer_is_special
            or type_to_special_nb[qtype_id]
            < int(special_limit_proportion * limit_per_qtype)
        ):
            row["info"]["question_type_identifier"] = qtype_id
            type_to_questions[qtype_id].append(row)
            if answer_is_special:
                type_to_special_nb[qtype_id] += 1

    new_examples = []
    for rows in type_to_questions.values():
        new_examples += rows

    return Dataset.from_list(new_examples)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model-id", type=str)
    parser.add_argument("-s", "--system-prompt", type=str, default=None)
    parser.add_argument("-e", "--eval-dataset", type=pl.Path)
    parser.add_argument("-l", "--examples-limit-per-question-type", type=int)
    parser.add_argument(
        "-u", "--base-url", type=str, default="http://localhost:8000/v1"
    )
    parser.add_argument("-k", "--api-key", type=str, default="dummy")
    parser.add_argument(
        "-f",
        "--filter",
        type=str,
        default=None,
        help="A Python expression to filter questions. Use the 'question' variable as a row of the dataset. For example, to keep only simple question, you can use: question['info']['question_level'] == 'simple'",
    )
    parser.add_argument(
        "-o", "--output-directory", type=pl.Path, default=pl.Path("./benchmark_output")
    )
    args = parser.parse_args()

    print(f"benchmark inference starting. Will save output in {args.output_directory}")
    os.makedirs(args.output_directory, exist_ok=True)

    test_dataset = load_test_dataset(
        args.eval_dataset, args.examples_limit_per_question_type
    )
    test_dataset.save_to_disk(args.output_directory / "eval_dataset")

    if not args.system_prompt is None:
        test_dataset = test_dataset.map(
            lambda example: adjust_system_prompt(example, args.system_prompt)
        )

    if not args.filter is None:
        test_dataset = test_dataset.filter(lambda question: eval(args.filter))

    preds = batched_inference(
        args.model_id,
        args.base_url,
        args.api_key,
        test_dataset["prompt"],
        test_dataset["info"],
    )
    labels = test_dataset["answer"]

    df_rows = [
        {
            "question": get_user_content(row["prompt"]),
            "question_level": row["info"]["question_level"],
            "answer_type": row["info"]["answer_type"],
            "question_type": row["info"]["question_type"],
            "temporal_relation": row["info"]["temporal_relation"],
            "label": label,
            "pred": pred,
        }
        for row, label, pred in zip(test_dataset, labels, preds)
    ]
    df = pd.DataFrame(df_rows)
    print(df)
    # we can't have a '/' in the model name
    safe_model_id = args.model_id.replace("/", ":")
    df.to_csv(args.output_directory / f"{safe_model_id}.csv", index=False, header=True)
