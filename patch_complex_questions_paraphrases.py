import json, copy, argparse
import pandas as pd
from tqdm import tqdm
from openai import OpenAI
from TimelineKGQA.openai_utils import paraphrase_medium_question


def patch_complex_questions_paraphrases(
    dataset: list[dict], client: OpenAI | None
) -> list[dict]:
    cplx_questions = [q for q in dataset if q["question_level"] == "complex"]
    print(f"complex questions to patch: {len(cplx_questions)}")
    patched_dataset = []
    for question in tqdm(dataset):
        new_question = copy.deepcopy(question)
        if question["question_level"] == "complex":
            try:
                new_paraphrase = paraphrase_medium_question(
                    question["question"], alt_client=client
                )
            except Exception as e:
                qid = question["id"]
                print(f"error generating paraphrase for question {qid}: {e}")
                continue
            new_question["paraphrased_question"] = new_paraphrase
        patched_dataset.append(new_question)
    return patched_dataset


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--client-base-url", type=str, default=None)
    parser.add_argument("-k", "--client-api-key", type=str, default=None)
    parser.add_argument(
        "-d",
        "--datasets",
        nargs="*",
        type=str,
        default=[],
        help="'icewsactor' or 'cronquestions'",
    )
    args = parser.parse_args()

    client = None
    if not args.client_base_url is None:
        client = OpenAI(base_url=args.client_base_url, api_key=args.client_api_key)

    dataset_setup = {
        "icewsactor": {
            "questions_path_json": "./Datasets/unified_kg_icews_actor_questions_all.json",
            "questions_path_csv": "./Datasets/unified_kg_icews_actor_questions_all.csv",
        },
        "cronquestions": {
            "questions_path_json": "./Datasets/unified_kg_cron_questions_all.json",
            "questions_path_csv": "./Datasets/unified_kg_cron_questions_all.csv",
        },
    }

    for dataset in args.datasets:
        # load both datasets
        with open(dataset_setup[dataset]["questions_path_json"]) as f:
            questions_dicts = json.load(f)
        questions_df = pd.read_csv(dataset_setup[dataset]["questions_path_csv"])

        # sanity check: we verify that the ids are in the same order for
        # both datasets since we are going to patch only one of them and
        # save in both formats
        assert all(
            dict["id"] == row["id"]
            for dict, (_, row) in zip(questions_dicts, questions_df.iterrows())
        )

        # patch dataset
        new_questions_dicts = patch_complex_questions_paraphrases(
            questions_dicts, client
        )

        # save datasets in json and csv
        with open(dataset_setup[dataset]["questions_path_json"], "w") as f:
            json.dump(new_questions_dicts, f)
        new_questions_df = pd.DataFrame(new_questions_dicts)
        new_questions_df.to_csv(
            dataset_setup[dataset]["questions_path_csv"], index=False, header=True
        )
