from typing import Literal
import shutil, os, pickle, sys, ast
from collections import defaultdict
from datetime import date, timedelta
import pathlib as pl
import torch
import pandas as pd
from pydantic import BaseModel, ValidationError
from torch_geometric.data import (
    Data,
    InMemoryDataset,
    download_google_url,
    extract_zip,
    download_url,
)
from tqdm import tqdm
from TimelineKGQA.agentic_retrieval.utils import DictTree


def id_to_entity(data: Data, entity_id: int | torch.Tensor) -> str:
    if isinstance(entity_id, torch.Tensor):
        entity_id = int(entity_id.item())
    return data.wikid_to_entity[data.id_to_entity_wikid[entity_id]]


def id_to_rel(data: Data, rel_id: int | torch.Tensor) -> str:
    if isinstance(rel_id, torch.Tensor):
        rel_id = int(rel_id.item())
    return data.wikid_to_relation[data.id_to_relation_wikid[rel_id]]


#                    subj pred obj  timestamp
Quad = tuple[str, str, str, tuple[str, str]]


def get_quads(data: Data, edge_mask: torch.Tensor) -> list[Quad]:
    """
    :param mask: a mask of shape (edge_nb,)
    """
    assert not data.edge_index is None
    indices = torch.nonzero(edge_mask).flatten()

    rel_ids = data.edge_rel[indices]
    entity_ids = data.edge_index[:, indices]
    subj_ids = entity_ids[0]
    obj_ids = entity_ids[1]
    timestamp_id = data.edge_timestamp_id[indices]
    quads = []

    for rel_id, subj_id, obj_id, ts_id in zip(rel_ids, subj_ids, obj_ids, timestamp_id):
        rel = id_to_rel(data, rel_id)
        subj = id_to_entity(data, subj_id)
        obj = id_to_entity(data, obj_id)
        ts = data.timestamps[ts_id]
        ts_start = str(ts[0].item())
        ts_end = str(ts[1].item())
        quads.append((subj, rel, obj, (ts_start, ts_end)))

    return quads


def load_id2name(path: pl.Path) -> dict[str, str]:
    id2name = {}
    with open(path) as f:
        for line in f:
            id_, name = line.strip("\n").split("\t")
            id2name[id_] = name
    return id2name


def load_cq_kg(path: str | pl.Path) -> list[Quad]:
    if isinstance(path, str):
        path = pl.Path(path)

    quads = []
    with open(path) as f:
        for line in f:
            subj, pred, obj, ts_start, ts_end = line.strip("\n").split("\t")
            quads.append((subj, pred, obj, (ts_start, ts_end)))

    return quads


CronQuestionType = Literal[
    "time_join", "first_last", "simple_time", "before_after", "simple_entity"
]


class CronQuestionsDataset(InMemoryDataset):
    """The CronQuestions dataset"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load(self.processed_paths[0])

    @property
    def raw_file_names(self) -> list[str]:
        return [
            "train.txt",
            "valid.txt",
            "test.txt",
            "train.pickle",
            "valid.pickle",
            "test.pickle",
            "wd_id2entity_text.txt",
            "wd_id2relation_text.txt",
        ]

    @property
    def processed_file_names(self) -> list[str]:
        return ["data.pt"]

    def download(self):
        raw_dir = pl.Path(self.raw_dir)
        gdown_out_path = raw_dir / "data_v2.zip"

        download_google_url(
            "1fe7-x7ChszqzczKncoZcpwmWc1PBq1_0", self.raw_dir, str(gdown_out_path.name)
        )
        extract_zip(str(gdown_out_path), str(raw_dir / "CronQuestions"))
        os.remove(gdown_out_path)

        kg_dir = raw_dir / "CronQuestions" / "data" / "wikidata_big" / "kg"
        shutil.move(kg_dir / "train", raw_dir / "train.txt")
        shutil.move(kg_dir / "valid", raw_dir / "valid.txt")
        shutil.move(kg_dir / "test", raw_dir / "test.txt")
        shutil.move(kg_dir / "wd_id2entity_text.txt", raw_dir / "wd_id2entity_text.txt")
        shutil.move(
            kg_dir / "wd_id2relation_text.txt", raw_dir / "wd_id2relation_text.txt"
        )

        questions_dir = (
            raw_dir / "CronQuestions" / "data" / "wikidata_big" / "questions"
        )
        shutil.move(questions_dir / "train.pickle", raw_dir / "train.pickle")
        shutil.move(questions_dir / "valid.pickle", raw_dir / "valid.pickle")
        shutil.move(questions_dir / "test.pickle", raw_dir / "test.pickle")

        shutil.rmtree(raw_dir / "CronQuestions")

    def process(self):
        raw_dir = pl.Path(self.raw_dir)

        ent_wikid2id = {}
        ent_next_id = 0
        rel_wikid2id = {}
        rel_next_id = 0
        edge_index = []
        edge_rel = []
        # { ts => id }
        timestamps = {}
        timestamp_next_id = 0
        edge_timestamp_id = []
        for split in ["train", "valid", "test"]:
            quads = load_cq_kg(raw_dir / f"{split}.txt")

            for subj, pred, obj, ts in tqdm(quads, ascii=True, desc=split):
                subj_id = ent_wikid2id.get(subj, ent_next_id)
                ent_wikid2id[subj] = subj_id
                if subj_id == ent_next_id:
                    ent_next_id += 1

                obj_id = ent_wikid2id.get(obj, ent_next_id)
                ent_wikid2id[obj] = obj_id
                if obj_id == ent_next_id:
                    ent_next_id += 1

                rel_id = rel_wikid2id.get(pred, rel_next_id)
                rel_wikid2id[pred] = rel_id
                if rel_id == rel_next_id:
                    rel_next_id += 1

                edge_rel.append(rel_id)
                edge_index.append([subj_id, obj_id])

                ts = (int(ts[0]), int(ts[1]))
                ts_id = timestamps.get(ts, timestamp_next_id)
                if ts_id == timestamp_next_id:
                    timestamps[ts] = ts_id
                    timestamp_next_id += 1
                edge_timestamp_id.append(ts_id)

        x = torch.tensor(list(ent_wikid2id.values()), dtype=torch.long)
        edge_index = torch.tensor(edge_index).t().contiguous()
        edge_rel = torch.tensor(edge_rel, dtype=torch.long)
        timestamps = torch.tensor(list(timestamps.keys()))
        edge_timestamp_id = torch.tensor(edge_timestamp_id, dtype=torch.long)

        wikid_to_entity = load_id2name(raw_dir / "wd_id2entity_text.txt")
        id_to_entity_wikid = {id_: wikid for wikid, id_ in ent_wikid2id.items()}

        wikid_to_relation = load_id2name(raw_dir / "wd_id2relation_text.txt")
        id_to_relation_wikid = {id_: wikid for wikid, id_ in rel_wikid2id.items()}

        self.questions = []
        split_len = {}
        for split in ["train", "valid", "test"]:
            with open(raw_dir / f"{split}.pickle", "rb") as f:
                split_questions = pickle.load(f)
            self.questions += split_questions
            split_len[split] = len(split_questions)
        self.train_mask = torch.tensor(
            [True] * split_len["train"]
            + [False] * (split_len["valid"] + split_len["test"])
        )
        self.valid_mask = torch.tensor(
            [False] * split_len["train"]
            + [True] * split_len["valid"]
            + [False] * split_len["test"]
        )
        self.test_mask = torch.tensor(
            [False] * (split_len["train"] + split_len["valid"])
            + [True] * split_len["test"]
        )

        data = Data(
            x=x,
            edge_index=edge_index,
            edge_rel=edge_rel,
            timestamps=timestamps,
            edge_timestamp_id=edge_timestamp_id,
            questions=self.questions,
            train_mask=self.train_mask,
            valid_mask=self.valid_mask,
            test_mask=self.test_mask,
            id_to_entity_wikid=id_to_entity_wikid,
            id_to_relation_wikid=id_to_relation_wikid,
            wikid_to_entity=wikid_to_entity,
            wikid_to_relation=wikid_to_relation,
            wikid_to_entity_id={v: k for k, v in id_to_entity_wikid.items()},
        )

        if self.pre_filter is not None:
            data = self.pre_filter(data)

        if self.pre_transform is not None:
            data = self.pre_transform(data)

        self.save([data], self.processed_paths[0])

    def id_to_entity(self, entity_id: int | torch.Tensor) -> str:
        return id_to_entity(self._data, entity_id)

    def id_to_rel(self, rel_id: int | torch.Tensor) -> str:
        return id_to_rel(self._data, rel_id)

    def get_quads(self, edge_mask: torch.Tensor) -> list[Quad]:
        return get_quads(self._data, edge_mask)


class TKGQAQuestion(BaseModel):
    id: int
    source_kg_id: int
    question: str
    answer: str
    paraphrased_question: str
    events: list[str]
    question_level: str
    question_type: str
    answer_type: str
    temporal_relation: str
    split: Literal["train", "test", "validation"]

    @staticmethod
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

    @staticmethod
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

    @property
    def coarse_answer_type(self) -> Literal["temporal", "factual"]:
        return TKGQAQuestion.get_coarse_answer_type(self.answer_type)

    @property
    def coarse_temporal_relation(
        self,
    ) -> Literal["timeline", "allen", "union/intersection", "ranking", "duration"]:
        return TKGQAQuestion.get_coarse_temporal_relation(self.temporal_relation)


torch.serialization.add_safe_globals([TKGQAQuestion])


class TKGQAFact(BaseModel):
    id: int
    subject: str
    subject_json: dict
    predicate: str
    predicate_json: dict
    object: str
    object_json: dict
    # in number of day since 0001-01-01
    start_time: int
    end_time: int


def gregorian_ts(date_str: str) -> int | None:
    """Convert a date to the number of days since 0001-01-01

    :param date_str: date in a YYYY-MM-DD format.  Also accept the
        following special values:

            - 'end of time', which is converted to 9999-12-31.

            - 'beginning of time', which is converted to 0001-01-01
    """
    if date_str == "end of time":
        date_str = "9999-12-31"
    elif date_str == "beginning of time":
        date_str = "0001-01-01"
    year, month, day = date_str.split("-")
    if int(year) < 1:  # not handled by datetime.date
        return None
    epoch = date(1, 1, 1)
    return (date(int(year), int(month), int(day)) - epoch).days


def date_from_gregorian_ts(ts: int) -> str:
    """
    :param ts: timestamp, in number of days since 0001-01-01.  Two
        values are treated specially to be symmetric with
        :func:`gregorian_ts`:

            - 9999-12-31: returns 'end of time'

            - 0001-01-01: returns 'beginning of time'
    """
    epoch = date(1, 1, 1)
    dt = timedelta(days=ts)
    if dt.days == 0:
        return "beginning of time"
    elif dt.days == (date(9999, 12, 31) - epoch).days:
        return "end of time"
    return (epoch + timedelta(days=ts)).strftime("%Y-%m-%d")


class TKGQADataset(InMemoryDataset):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load(self.processed_paths[0])

    @property
    def processed_file_names(self) -> list[str]:
        return ["data.pt"]

    def download(self):
        raw_dir = pl.Path(self.raw_dir)
        download_url(
            "https://github.com/Aethor/TimelineKGQA/archive/refs/heads/patch-questions.zip",
            self.raw_dir,
        )
        branch = "patch-questions"
        extract_zip(str(raw_dir / f"{branch}.zip"), self.raw_dir)
        os.remove(raw_dir / f"{branch}.zip")
        shutil.move(
            raw_dir / f"TimelineKGQA-{branch}" / "Datasets" / "unified_kg_cron.csv",
            raw_dir / "unified_kg_cron.csv",
        )
        shutil.move(
            raw_dir
            / f"TimelineKGQA-{branch}"
            / "Datasets"
            / "unified_kg_cron_questions_all.csv",
            raw_dir / "unified_kg_cron_questions_all.csv",
        )
        shutil.move(
            raw_dir
            / f"TimelineKGQA-{branch}"
            / "Datasets"
            / "unified_kg_icews_actor_v2.csv",
            raw_dir / "unified_kg_icews_actor_v2.csv",
        )
        shutil.move(
            raw_dir
            / f"TimelineKGQA-{branch}"
            / "Datasets"
            / "unified_kg_icews_actor_questions_all_v2.csv",
            raw_dir / "unified_kg_icews_actor_questions_all_v2.csv",
        )
        shutil.rmtree(raw_dir / f"TimelineKGQA-{branch}")

    def _tkgqa_process(self, kg_csv_path: pl.Path, questions_csv_path: pl.Path):
        # 1. load questions
        questions: list[TKGQAQuestion] = []
        wrongly_formatted_questions_nb = 0
        questions_df = pd.read_csv(questions_csv_path)
        for _, elt in tqdm(
            questions_df.iterrows(),
            ascii=True,
            desc="questions",
            total=len(questions_df),
        ):
            elt.events = list(ast.literal_eval(elt.events))
            try:
                tkgqa_question = TKGQAQuestion(**elt)
            except ValidationError:
                wrongly_formatted_questions_nb += 1
                continue
            questions.append(tkgqa_question)
        print(
            f"Skipped {wrongly_formatted_questions_nb} wrongly formatted questions.",
            file=sys.stderr,
        )
        if wrongly_formatted_questions_nb == len(questions_df):
            print("No questions were loaded, something must be wrong.")
            try:
                tkgqa_question = TKGQAQuestion(**elt)
            except ValidationError as e:
                print("One of the error is:")
                print(e)
            print("Entering debugger.")
            breakpoint()

        # 2. load KG
        nodes: dict[str, int] = {}
        nodes_nb = 0
        entity_aliases = defaultdict(list)  # { alias => entity }
        edge_index = []
        edge_rel_id: dict[str, int] = {}
        edge_rel = []
        edge_rel_nb = 0
        edge_ts_start = []
        edge_ts_end = []

        kg_df = pd.read_csv(kg_csv_path)

        for _, elt in tqdm(kg_df.iterrows(), ascii=True, desc="KG", total=len(kg_df)):
            if elt["object"] is None:  # rare data error
                continue
            # we use int (the number of days since 0001-01-01) to
            # store dates, in order to compute fast ordering.
            elt["start_time"] = gregorian_ts(elt["start_time"])
            elt["end_time"] = gregorian_ts(elt["end_time"])
            if elt["start_time"] is None or elt["end_time"] is None:
                continue
            elt["subject_json"] = ast.literal_eval(elt["subject_json"])
            elt["predicate_json"] = ast.literal_eval(elt["predicate_json"])
            elt["object_json"] = ast.literal_eval(elt["object_json"])
            fact = TKGQAFact(**elt)

            subject_id = nodes.get(fact.subject, nodes_nb)
            if subject_id == nodes_nb:
                nodes[fact.subject] = nodes_nb
                nodes_nb += 1
            object_id = nodes.get(fact.object, nodes_nb)
            if object_id == nodes_nb:
                nodes[fact.object] = nodes_nb
                nodes_nb += 1

            if "Aliases" in fact.subject_json:
                aliases = fact.subject_json["Aliases"].split(" || ")
                for alias in aliases:
                    entity_aliases[alias.lower()].append(fact.subject)
            if "Aliases" in fact.object_json:
                aliases = fact.object_json["Aliases"].split(" || ")
                for alias in aliases:
                    entity_aliases[alias.lower()].append(fact.object)

            edge_index.append((subject_id, object_id))

            rel_id = edge_rel_id.get(fact.predicate, edge_rel_nb)
            if rel_id == edge_rel_nb:
                edge_rel_id[fact.predicate] = edge_rel_nb
                edge_rel_nb += 1
            edge_rel.append(rel_id)

            edge_ts_start.append(fact.start_time)
            edge_ts_end.append(fact.end_time)

        x = torch.tensor(list(nodes.values()), dtype=torch.long)
        edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous()
        edge_rel = torch.tensor(edge_rel, dtype=torch.long)
        edge_ts_start = torch.tensor(edge_ts_start)
        edge_ts_end = torch.tensor(edge_ts_end)

        # 3. save dataset
        data = Data(
            x=x,
            entity_to_id=nodes,
            entity_aliases=entity_aliases,
            id_to_entity={v: k for k, v in nodes.items()},
            edge_index=edge_index,
            edge_rel=edge_rel,
            rel_to_id=edge_rel_id,
            id_to_rel={v: k for k, v in edge_rel_id.items()},
            edge_ts_start=edge_ts_start,
            edge_ts_end=edge_ts_end,
            train=[q for q in questions if q.split == "train"],
            dev=[q for q in questions if q.split == "validation"],
            test=[q for q in questions if q.split == "test"],
        )
        if self.pre_filter is not None:
            data = self.pre_filter(data)
        if self.pre_transform is not None:
            data = self.pre_transform(data)
        self.save([data], self.processed_paths[0])

    def process(self):
        raise NotImplementedError

    def entities_from_alias(self, alias: str) -> list[str]:
        return self.entity_aliases[alias.lower()]

    def print_hierarchy_tree(self):
        # hierarchical tree
        # question_level -> answer_type -> question_type -> temporal_relation
        tree = DictTree()
        questions: list[TKGQAQuestion] = self.train + self.dev + self.test
        for question in questions:
            ql = question.question_level
            at = question.answer_type
            qt = question.question_type
            tr = question.coarse_temporal_relation
            tree[ql][at][qt][tr] += 1
        tree.print_hierarchy()


class TKGQACronQuestionsDataset(TKGQADataset):
    @property
    def raw_file_names(self) -> list[str]:
        return [
            "unified_kg_cron.csv",
            "unified_kg_cron_questions_all.csv",
        ]

    def process(self):
        raw_dir = pl.Path(self.raw_dir)
        return self._tkgqa_process(
            raw_dir / "unified_kg_cron.csv",
            raw_dir / "unified_kg_cron_questions_all.csv",
        )


class TKGQAIcewsActorDataset(TKGQADataset):
    @property
    def raw_file_names(self) -> list[str]:
        return [
            "unified_kg_icews_actor_v2.csv",
            "unified_kg_icews_actor_questions_all_v2.csv",
        ]

    def process(self):
        raw_dir = pl.Path(self.raw_dir)
        return self._tkgqa_process(
            raw_dir / "unified_kg_icews_actor_v2.csv",
            raw_dir / "unified_kg_icews_actor_questions_all_v2.csv",
        )
