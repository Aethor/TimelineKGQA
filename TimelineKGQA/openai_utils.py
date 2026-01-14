from scratch import paraphrased
from typing import Mapping

from openai import OpenAI

from TimelineKGQA.templates import get_paraphrase_examples
from TimelineKGQA.utils import get_logger

logger = get_logger(__name__)

coarse_answer_type = {
    "timestamp_end": "timestamp",
    "timestamp_start": "timestamp",
    "relation_duration": "duration",
    "duration": "duration",
    "relation_ranking": "ranking",
    "subject": "entity",
    "object": "entity",
    "timestamp_range": "time interval",
    "relation_union_or_intersection": "time interval",
}


def paraphrase_question(question: Mapping, client: OpenAI, model_name: str) -> str:
    """
    Paraphrases the given question using the OpenAI model specified.

    Args:
        question (str): The question to paraphrase.

        model_name (str): The model to use for paraphrasing.

    Returns:
        str: The paraphrased question.
    """
    prompt_text = "Paraphrase the following question: '{}'".format(question["question"])

    examples = get_paraphrase_examples(question)
    examples_str = []
    for raw_question, paraphrase in examples:
        examples_str.append(f"question: {raw_question}\nparaphrase: {paraphrase}\n")
    examples_str = "\n".join(examples_str)

    try:
        # Some examples include:
        # Who is affiliated with the organization during a given time.
        # Which or what's the organization's name a specific guy is affiliated to.
        # When/During/when is start time ...
        # Etc.
        # If there is a statement from beginning of time to the end of time, this will mean it is always true for the whole timeline.
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert on paraphrasing questions.
                    You job is paraphrasing this question into a natural language question.
                    The answer to this question is a {}: {}.
                    Do not mention the answer in the question.
                    You must mention all temporal constraints of the question.
                    Do not add additional time indication in the question, it is a type of implicit temporal question.
                    Only output the paraphrase of the question and nothing else.

                    Example(s):
                    {}
                    """.format(
                        coarse_answer_type.get(
                            question["answer_type"], question["answer_type"]
                        ),
                        question["answer"],
                        examples_str,
                    ),
                },
                {
                    "role": "user",
                    "content": prompt_text,
                },
            ],
            max_tokens=100,
            temperature=0.8,
            stop=["\n"],
        )
        paraphrased_question = response.choices[0].message.content
        if question["answer"] in paraphrased_question:
            raise ValueError(
                "the question in invalid because the answer was found in the question"
            )
        return paraphrased_question
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""


def embedding_content(prompt, model_name="text-embedding-3-small"):
    """
    Args:
        prompt: The prompt to generate the embedding for
        model_name: The model to use for generating the embedding

    """
    response = client.embeddings.create(input=prompt, model=model_name)

    return response.data[0].embedding
