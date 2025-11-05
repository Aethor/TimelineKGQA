import json, copy, argparse
import pandas as pd
from tqdm import tqdm
from openai import OpenAI
from TimelineKGQA.openai_utils import paraphrase_medium_question


def patch_complex_questions_paraphrases(
    dataset: list[dict], client: OpenAI | None
) -> list[dict]:
    patched_dataset = []
    for question in tqdm(dataset):
        try:
            new_paraphrase = paraphrase_medium_question(
                question["question"], alt_client=client
            )
        except Exception as e:
            qid = question["id"]
            print(f"error generating paraphrase for question {qid}: {e}")
            continue
        new_question = copy.deepcopy(question)
        new_question["paraphrased_question"] = new_paraphrase
        patched_dataset.append(new_question)
    return patched_dataset


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--client-base-url", type=str, default=None)
    parser.add_argument("-k", "--client-api-key", type=str, default=None)
    args = parser.parse_args()

    client = None
    if not args.client_base_url is None:
        client = OpenAI(base_url=args.client_base_url, api_key=args.client_api_key)

    # load both datasets
    with open("./Datasets/unified_kg_cron_questions_all.json") as f:
        cron_questions_dicts = json.load(f)
    cron_questions_df = pd.read_csv("./Datasets/unified_kg_cron_questions_all.csv")
    with open("./Datasets/unified_kg_icews_actor_questions_all.json") as f:
        icews_questions_dicts = json.load(f)
    icews_questions_df = pd.read_csv(
        "./Datasets/unified_kg_icews_actor_questions_all.csv"
    )

    # sanity check: we verify that the ids are in the same order for
    # both datasets since we are going to patch only one of them and
    # save it in both formats
    assert all(
        dict["id"] == row["id"]
        for dict, (_, row) in zip(cron_questions_dicts, cron_questions_df.iterrows())
    )
    assert all(
        dict["id"] == row["id"]
        for dict, (_, row) in zip(icews_questions_dicts, icews_questions_df.iterrows())
    )

    # patch dataset
    new_cron_questions_dicts = patch_complex_questions_paraphrases(
        cron_questions_dicts, client
    )
    new_icews_questions_dicts = patch_complex_questions_paraphrases(
        icews_questions_dicts, client
    )

    # save both datasets in json and csv
    with open("./Datasets/unified_kg_cron_questions_all.json", "w") as f:
        json.dump(new_cron_questions_dicts, f)
    new_cron_questions_df = pd.DataFrame(new_cron_questions_dicts)
    new_cron_questions_df.to_csv(
        "./Datasets/unified_kg_cron_questions_all.csv", index=False, header=True
    )

    with open("./Datasets/unified_kg_icews_actor_questions_all.json") as f:
        json.dump(new_icews_questions_dicts, f)
    new_icews_questions_df = pd.DataFrame(new_icews_questions_dicts)
    new_icews_questions_df.to_csv(
        "./Datasets/unified_kg_icews_actor_questions_all.csv", index=False, header=True
    )
