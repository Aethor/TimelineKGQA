from typing import Literal, Callable
import argparse, re, ast, math, json
import pathlib as pl
import pandas as pd
from collections import defaultdict
from datasets import Dataset
from datasets import load_from_disk, Dataset
from datetime import timedelta, datetime
import evaluate
from tqdm import tqdm
from benchmark_inference import ChatMessage, get_user_content
from TimelineKGQA.agentic_retrieval.pyg_datasets import TKGQAQuestion


def parse_model_output(output: str) -> str:
    def get_boxed_content(i: int) -> str:
        content = []
        brace_counter = 1
        while brace_counter != 0 and i < len(output):
            if output[i] == "{":
                brace_counter += 1
            elif output[i] == "}":
                brace_counter -= 1
            if brace_counter != 0:
                content.append(output[i])
            i += 1
        if brace_counter != 0:
            return ""
        return "".join(content)

    matches = list(re.finditer(r"\\boxed{", output, re.DOTALL))
    if len(matches) == 0:
        return ""
    return get_boxed_content(matches[-1].end())


Info = dict[
    Literal["question_level", "answer_type", "question_type", "temporal_relation"], str
]
Metric = Callable[[list[ChatMessage], str, Info], float | int]


def make_exact_accuracy(**kwargs) -> Metric:
    def exact_accuracy(completion: list[ChatMessage], answer: str, info: Info) -> int:
        assert "content" in completion[-1]
        output = parse_model_output(completion[-1]["content"])
        return 1 if output.lower().strip() == answer.lower().strip() else 0

    return exact_accuracy


def make_tools_calls_nb(**kwargs) -> Metric:
    def tool_calls_nb(completion: list[ChatMessage], answer: str, info: Info) -> int:
        return sum(1 if m["role"] == "tool" else 0 for m in completion)

    return tool_calls_nb


def make_bleu(**kwargs) -> Metric:
    bleu_metric = evaluate.load("bleu")

    def bleu(completion: list[ChatMessage], answer: str, info: Info) -> float:
        assert "content" in completion[-1]
        output = parse_model_output(completion[-1]["content"])
        if len(answer) == 0 or len(output.strip()) == 0:
            return float("nan")
        result = bleu_metric.compute(
            predictions=[output], references=[[answer]], smooth=True
        )  # type: ignore
        return result["bleu"]  # type: ignore

    return bleu


def make_bertscore(**kwargs) -> Metric:
    bert_score_metric = evaluate.load("bertscore")

    def bertscore(completion: list[ChatMessage], answer: str, info: Info) -> float:
        assert "content" in completion[-1]
        output = parse_model_output(completion[-1]["content"])
        if len(output.strip()) == 0:
            return 0.0
        if len(answer) == 0 or len(completion) == 0:
            return float("nan")
        result = bert_score_metric.compute(
            predictions=[output], references=[answer], lang="en"
        )
        return result["f1"][0]  # type: ignore

    return bertscore


def make_timestamp_delta(model: str, api_base: str, api_key: str, **kwargs) -> Metric:
    import dspy

    class Timestamp(dspy.Signature):
        text: str = dspy.InputField()
        timestamp: str = dspy.OutputField(
            desc="The timestamp in the input text in YYYY-MM-DD format, or one of the special values 'beginning of time', 'end time' or 'invalid'."
        )
        contains_valid_timestamp: int = dspy.OutputField(
            desc="Whether the text contains a valid timestamp or not"
        )

    examples = [
        dspy.Example(
            text="2021 December 1st", timestamp="2021-12-01", contains_valid_date=True
        ),
        dspy.Example(
            text="the beginning of time",
            timestamp="beginning of time",
            contains_valid_date=True,
        ),
        dspy.Example(
            text="no information available",
            timestamp="invalid",
            contains_valid_date=False,
        ),
    ]

    ts_extractor = dspy.Predict(Timestamp, demos=examples)

    def timestamp_delta(
        completion: list[ChatMessage], answer: str, info: Info
    ) -> float:
        if not info["answer_type"] in {"timestamp_start", "timestamp_end"}:
            return float("nan")

        assert "content" in completion[-1]
        output = parse_model_output(completion[-1]["content"])

        with dspy.context(lm=dspy.LM(model=model, api_base=api_base, api_key=api_key)):
            maybe_output_ts = ts_extractor(text=output)
            if not maybe_output_ts.contains_valid_timestamp:
                return float("nan")

        if answer in {
            "beginning of time",
            "end of time",
        } or maybe_output_ts.timestamp in {"beginning of time", "end of time"}:
            return 0 if answer == maybe_output_ts.timestamp else float("inf")

        output_ts = datetime.strptime(maybe_output_ts.timestamp, "%Y-%m-%d")
        answer_ts = datetime.strptime(answer, "%Y-%m-%d")
        return (answer_ts - output_ts).days

    return timestamp_delta


def make_duration_delta(model: str, api_base: str, api_key: str, **kwargs) -> Metric:
    import dspy

    class Duration(dspy.Signature):
        text: str = dspy.InputField()
        years: int = dspy.OutputField(desc="Number of years in the input text.")
        months: int = dspy.OutputField(desc="Number of months in the input text.")
        days: int = dspy.OutputField(desc="Number of days in the input text.")
        is_infinite: bool = dspy.OutputField(
            desc="Whether the duration in the text is infinite."
        )
        contains_duration: bool = dspy.OutputField(
            desc="Whether the text contains a valid duration. An infinite duration is a valid duration."
        )

    examples = [
        dspy.Example(
            text="3 years",
            years=3,
            months=0,
            days=0,
            is_infinite=False,
            contains_duration=True,
        ),
        dspy.Example(
            text="1 year 2 months 3 days",
            years=1,
            months=2,
            days=3,
            is_infinite=False,
            contains_duration=True,
        ),
        dspy.Example(
            text="Infinite",
            years=0,
            months=0,
            days=0,
            is_infinite=True,
            contains_duration=True,
        ),
        dspy.Example(
            text="no information",
            years=0,
            months=0,
            days=0,
            is_infinite=False,
            contains_duration=False,
        ),
        dspy.Example(
            text="Indefinite",
            years=0,
            months=0,
            days=0,
            is_infinite=False,
            contains_duration=False,
        ),
    ]

    duration_extractor = dspy.Predict(Duration, demos=examples)

    def parse_answer_duration(duration: str) -> float:
        m = re.match(r"([0-9]+) years, ([0-9]+) months, ([0-9])+ days.*", duration)
        try:
            years, months, days = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except AttributeError:
            return float("nan")
        return 365 * years + 30 * months + days

    def duration_delta(completion: list[ChatMessage], answer: str, info: Info) -> float:
        if not info["answer_type"] in {"duration", "relation_duration"}:
            return float("nan")

        assert "content" in completion[-1]
        output = parse_model_output(completion[-1]["content"])

        with dspy.context(lm=dspy.LM(model=model, api_base=api_base, api_key=api_key))
            maybe_output_duration = duration_extractor(text=output)
            if not maybe_output_duration.contains_duration:
                return float("nan")

        if maybe_output_duration.is_infinite and answer != "forever":
            return float("inf")
        if answer == "forever" and maybe_output_duration.is_infinite:
            return float("inf")

        output_duration = timedelta(
            days=maybe_output_duration.years * 365
            + maybe_output_duration.months * 30
            + maybe_output_duration.days
        )
        answer_duration = parse_answer_duration(answer)
        if math.isnan(answer_duration):
            return float("nan")
        answer_duration = timedelta(days=parse_answer_duration(answer))

        return (answer_duration - output_duration).days

    return duration_delta


def make_interval_overlap(model: str, api_base: str, api_key: str, **kwargs) -> Metric:
    import dspy

    class Interval(dspy.Signature):
        text: str = dspy.InputField()
        interval_start: str = dspy.OutputField(
            desc="The start of the interval in the input text in YYYY-MM-DD format, or one of the special values 'beginning of time', 'invalid'"
        )
        interval_end: str = dspy.OutputField(
            desc="The end of the interval in the input text in YYYY-MM-DD format, or one of the special values 'beginning of time', 'invalid'"
        )
        contains_valid_interval: bool = dspy.OutputField(
            desc="Whether the input text contains a valid interval or not."
        )

    examples = [
        dspy.Example(
            text="beginning of time to 1999-12-01",
            interval_start="beginning of time",
            interval_end="1999-12-01",
            contains_valid_interval=True,
        ),
        dspy.Example(
            text="no information available",
            interval_start="invalid",
            interval_end="invalid",
            contains_valid_interval=False,
        ),
    ]

    interval_extractor = dspy.Predict(Interval, demos=examples)

    def interval_overlap(
        completion: list[ChatMessage], answer: str, info: Info
    ) -> float:
        if not info["answer_type"] == "timestamp_range":
            return float("nan")

        assert "content" in completion[-1]
        output = parse_model_output(completion[-1]["content"])

        with dspy.context(lm=dspy.LM(model=model, api_base=api_base, api_key=api_key)):
            out = interval_extractor(text=output)
            if not out.contains_valid_interval:
                return float("nan")

        answer_start, answer_end = answer.split(" and ")

        if (
            answer_start == "beginning of time"
            or answer_end == "end of time"
            or out.interval_start == "beginning of time"
            or out.interval_start == "end of time"
        ):
            return (
                1
                if answer_start == out.interval_start and answer_end == out.interval_end
                else 0
            )

        try:
            out_start = datetime.strptime(out.interval_start, "%Y-%m-%d")
            out_end = datetime.strptime(out.interval_end, "%Y-%m-%d")
        except ValueError:
            return float("nan")
        answer_start = datetime.strptime(answer_start, "%Y-%m-%d")
        answer_end = datetime.strptime(answer_end, "%Y-%m-%d")

        union = (max(answer_end, out_end) - min(answer_start, out_start)).days
        if union == 0:
            return 0

        intersection = (min(answer_end, out_end) - max(answer_start, out_start)).days
        intersection = max(intersection, 0)

        return intersection / union

    return interval_overlap


def make_llm_judge(model: str, api_base: str, api_key: str, **kwargs) -> Metric:
    import dspy

    class JudgeAnswer(dspy.Signature):
        question: str = dspy.InputField()
        assistant_answer: str = dspy.InputField()
        reference_answer: str = dspy.InputField()
        assistant_is_correct: bool = dspy.OutputField()

    examples = [
        dspy.Example(
            question="Who was President of France from 2007 to 2012?",
            assistant_answer="President Nicolas Sarkozy",
            reference_answer="Nicolas Sarkozy",
            assistant_is_correct=True,
        ),
        dspy.Example(
            question="Who was President of France from 2012 to 2017?",
            assistant_answer="President Jacques Chirac",
            reference_answer="François Hollande",
            assistant_is_correct=False,
        ),
    ]

    judge = dspy.Predict(JudgeAnswer, demos=examples)

    def llm_judge(completion: list[ChatMessage], answer: str, info: Info) -> float:
        assert "content" in completion[-1]
        instruction = get_user_content(completion)
        output = parse_model_output(completion[-1]["content"])
        if len(output.strip()) == 0:
            return 0.0
        if output.lower() == answer.lower():
            return 1.0
        with dspy.context(lm=dspy.LM(model=model, api_base=api_base, api_key=api_key)):
            judge_output = judge(
                question=instruction, assistant_answer=output, reference_answer=answer
            )
        return 1 if judge_output.assistant_is_correct else 0

    return llm_judge


METRICS = [
    ("bleu", make_bleu),
    ("tool_calls_nb", make_tools_calls_nb),
    ("bertscore", make_bertscore),
    ("exact_accuracy", make_exact_accuracy),
    ("llm_judge", make_llm_judge),
    ("duration_delta", make_duration_delta),
    ("timestamp_delta", make_timestamp_delta),
    ("interval_overlap", make_interval_overlap),
]


def compute_metrics(
    completions: list[list[ChatMessage]],
    answers: list[str],
    info_list: list[Info],
    metric_filter: list[str] | None,
    metric_kwargs: dict,
) -> dict[str, list[float | int]]:
    metrics_dict = defaultdict(list)

    # kwargs to send to all metrics
    global_kwargs = {k: v for k, v in metric_kwargs.items() if not isinstance(v, dict)}

    for metric_name, metric_creator in METRICS:
        if not metric_filter is None and not metric_name in metric_filter:
            continue

        # merge metric-specific kwargs with global kwargs
        kwargs = {**global_kwargs, **metric_kwargs.get(metric_name, {})}

        try:
            metric_fn = metric_creator(**kwargs)
        except Exception as e:
            print(f"[warning] metric {metric_name} creation failed for: {repr(e)}")
            continue

        for completion, answer, info in tqdm(
            zip(completions, answers, info_list),
            total=len(completions),
            desc=metric_name,
        ):
            try:
                metric_value = metric_fn(completion, answer, info)
            except Exception as e:
                tqdm.write(
                    f"[warning] metric {metric_name} computation failed: {repr(e)}"
                )
                metric_value = float("nan")
            metrics_dict[metric_name].append(metric_value)

        del metric_fn

    return metrics_dict


def get_question_type_identifier(row: dict) -> tuple:
    info = row["info"]
    return (
        ("question_level", info["question_level"]),
        ("answer_type", TKGQAQuestion.get_coarse_answer_type(info["answer_type"])),
        ("question_type", info["question_type"]),
        (
            "temporal_relation",
            TKGQAQuestion.get_coarse_temporal_relation(info["temporal_relation"]),
        ),
    )


def load_test_dataset(base_dataset_path: str, limit_per_qtype: int) -> Dataset:
    test = load_from_disk(base_dataset_path)["test"]

    type_to_questions = defaultdict(list)
    for row in test:
        qtype_id = get_question_type_identifier(row)  # type: ignore
        if len(type_to_questions[qtype_id]) < limit_per_qtype:
            row["info"]["question_type_identifier"] = qtype_id
            type_to_questions[qtype_id].append(row)

    new_examples = []
    for rows in type_to_questions.values():
        new_examples += rows

    return Dataset.from_list(new_examples)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-i", "--input-file", type=pl.Path)
    parser.add_argument(
        "-u",
        "--base-url",
        type=str,
        default="http://localhost:8000/v1",
        help="URL for OpenAI compatible service for LLM-based metrics.",
    )
    parser.add_argument(
        "-k",
        "--api-key",
        type=str,
        default="dummy",
        help="API key for OpenAI compatible service for LLM-based metrics.",
    )
    parser.add_argument(
        "-k",
        "--metric-kwargs",
        type=json.loads,
        default={
            "base_url": "http://localhost:8000/v1",
            "api_key": "dummy",
            "llm_judge": {"model": "hosted_vllm/google/gemma-3-8b-it"},
            "duration_delta": {"model": "hosted_vllm/google/gemma-3-8b-it"},
            "interval_delta": {"model": "hosted_vllm/google/gemma-3-8b-it"},
            "timestamp_delta": {"model": "hosted_vllm/google/gemma-3-8b-it"},
        },
        help="kwargs for each metric, as a json dictionary. Top-level keys indicate common configuration. Nested dictionaries indicate metric-specific dicts.",
    )
    parser.add_argument(
        "-m",
        "--metric-filter",
        nargs="*",
        default=None,
        help="list of metrics to compute (default: all)",
    )
    args = parser.parse_args()

    print(
        f"benchmark metrics computation starting. Will update output of {args.input_file}"
    )

    df = pd.read_csv(args.input_file)

    completions = [ast.literal_eval(chat) for chat in df["pred"]]
    labels = list(df["label"])

    info = df[
        ["answer_type", "question_type", "temporal_relation", "question_level"]
    ].to_dict("records")  # type: ignore
    metrics = compute_metrics(
        completions, labels, info, args.metric_filter, args.metric_kwargs
    )

    for metric_key, metric_values in metrics.items():
        df[metric_key] = metric_values

    df.to_csv(args.input_file, index=False, header=True)
