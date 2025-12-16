import argparse, random
import pandas as pd


def get_split(*args) -> str:
    rnd = random.random()
    if rnd <= 0.8:
        return "train"
    elif rnd < 0.9:
        return "validation"
    else:
        return "test"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-file", type=str)
    args = parser.parse_args()

    random.seed(0)
    df = pd.read_csv(args.input_file)
    df["split"] = df.apply(get_split, axis=1)
    df.to_csv(args.input_file)
