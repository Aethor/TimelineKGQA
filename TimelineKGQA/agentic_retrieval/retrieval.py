from typing import Literal, Callable, Optional
import re
import torch
from torch_geometric.data import Data
import dspy
from rapidfuzz import fuzz
from TimelineKGQA.agentic_retrieval.pyg_datasets import (
    TKGQADataset,
    TKGQACronQuestionsDataset,
    TKGQAIcewsActorDataset,
    date_from_gregorian_ts,
    gregorian_ts,
)
from TimelineKGQA.agentic_retrieval.tools import Tool, get_tool_dict


Quad = tuple[str, str, str, tuple[str, str]]


def _retrieve_with_constraints(
    data: Data,
    subj_ct: int | Literal["*"],
    rel_ct: int | Literal["*"],
    obj_ct: int | Literal["*"],
    ts_ct: tuple[int | Literal["*"], int | Literal["*"]],
) -> torch.Tensor:
    """Low level function to retrieve temporal facts with simple constraints.

    :param subj_ct: impose a constraint on the id of the subject entity (* for any entity)
    :param rel_ct: impose a constraint on the id of the relation (* for any relation)
    :param obj_ct: impose a constraint on the id of the object entity (* for any entity)
    :param ts_ct: impose a constraint on the timestamp (* for any timestamp)

    :return: a bool tensor of shape (edge_nb,)
    """
    assert not data.edge_index is None
    assert not data.edge_ts_start is None
    assert not data.edge_ts_end is None

    true_mask = torch.full(data.edge_rel.shape, True)

    subj_mask = data.edge_index[0] == subj_ct if subj_ct != "*" else true_mask
    rel_mask = data.edge_rel == rel_ct if rel_ct != "*" else true_mask
    obj_mask = data.edge_index[1] == obj_ct if obj_ct != "*" else true_mask
    start_mask = data.edge_ts_start >= ts_ct[0] if ts_ct[0] != "*" else true_mask
    end_mask = data.edge_ts_end <= ts_ct[1] if ts_ct[1] != "*" else true_mask

    return subj_mask & rel_mask & obj_mask & start_mask & end_mask


def quads_from_edge_mask(data: Data, edge_mask: torch.Tensor) -> list[Quad]:
    """
    :param mask: a mask of shape (edge_nb,)
    """
    assert not data.edge_index is None

    indices = torch.nonzero(edge_mask).flatten()
    rel_ids = data.edge_rel[indices]
    subj_ids = data.edge_index[0, indices]
    obj_ids = data.edge_index[1, indices]
    ts_start_lst = data.edge_ts_start[indices]
    ts_end_lst = data.edge_ts_end[indices]

    quads = []
    for subj_id, rel_id, obj_id, ts_start, ts_end in zip(
        subj_ids, rel_ids, obj_ids, ts_start_lst, ts_end_lst
    ):
        quads.append(
            (
                data.id_to_entity[subj_id.item()],
                data.id_to_rel[rel_id.item()],
                data.id_to_entity[obj_id.item()],
                (
                    date_from_gregorian_ts(ts_start.item()),
                    date_from_gregorian_ts(ts_end.item()),
                ),
            )
        )

    return quads


def retrieve_with_constraints(
    dataset: TKGQADataset,
    subj_ct: str | Literal["*"],
    rel_ct: str | Literal["*"],
    obj_ct: str | Literal["*"],
    ts_ct: tuple[str | Literal["*"], str | Literal["*"]],
) -> list[Quad]:
    # convert entity/relation/timestamp strings to int for tensor
    # retrieval with the low level function _retrieve_with_constraints
    subj_ct_id = dataset.entity_to_id[subj_ct] if subj_ct != "*" else "*"
    rel_ct_id = dataset.rel_to_id[rel_ct] if rel_ct != "*" else "*"
    obj_ct_id = dataset.entity_to_id[obj_ct] if obj_ct != "*" else "*"
    start = gregorian_ts(ts_ct[0]) if ts_ct[0] != "*" else "*"
    assert not start is None
    end = gregorian_ts(ts_ct[1]) if ts_ct[1] != "*" else "*"
    assert not end is None

    edge_mask = _retrieve_with_constraints(
        dataset._data,
        subj_ct_id,
        rel_ct_id,
        obj_ct_id,
        (start, end),
    )

    return quads_from_edge_mask(dataset._data, edge_mask)


class TKGQAQueryTool(Tool):
    def __init__(
        self,
        dataset_name: Literal["cronquestions", "icewsactor"],
        linking_style: Literal["exact", "fuzzy", "oracle"] = "exact",
        lm: dspy.LM | None = None,
        fuzzy_threshold: float = 80.0,
    ):
        if dataset_name == "cronquestions":
            self.kg = TKGQACronQuestionsDataset(
                root="./pyg_datasets/TKGQA_CronQuestions/"
            )
        elif dataset_name == "icewsactor":
            self.kg = TKGQAIcewsActorDataset(root="./pyg_datasets/TKGQA_IcewsActor/")
        else:
            raise ValueError(dataset_name)

        assert linking_style in {"exact", "fuzzy", "oracle"}
        self.linking_style = linking_style
        if self.linking_style == "fuzzy":
            self.relation_picker = dspy.Predict(
                dspy.Signature(
                    "candidate_relation, possible_relations -> relation: str",  # type: ignore
                    instructions="Given a candidate_relation, pick the closest possible relation amongst the possible_relations",
                )  # type: ignore
            )
            self.fuzzy_threshold = fuzzy_threshold
            self.candidates_selector = dspy.Predict(
                "entity_candidates, context -> entity: str",
                instructions="Given a context and a list of entity candidates, select the entity being referenced by the context",
            )
        else:
            self.relation_picker = None
            self.candidates_predictor = None

        self.lm = lm

    @staticmethod
    def format_query_knowledge_base_tool_call(
        subject: str | Literal["*"],
        relation: str | Literal["*"],
        object: str | Literal["*"],
        start: str | Literal["*"],
        end: str | Literal["*"],
    ) -> dict:
        return {
            "role": "assistant",
            "tool_calls": [
                {
                    "type": "function",
                    "function": {
                        "name": "query_knowledge_base",
                        "arguments": {
                            "subject": subject,
                            "relation": relation,
                            "object": object,
                            "start": start,
                            "end": end,
                        },
                    },
                }
            ],
        }

    def fuzzy_link_entity(self, mention: str, context: str) -> Optional[str]:
        """Resolve an entity using dspy"""
        assert not self.candidates_selector is None
        assert not self.lm is None

        # 1. generate candidates
        candidates: set[str] = set(self.kg.entities_from_alias(mention))
        if mention in self.kg.entity_to_id:
            candidates.add(mention)
        candidates |= {
            entity
            for entity in self.kg.entity_to_id.keys()
            if fuzz.ratio(mention, entity) > self.fuzzy_threshold
        }
        candidates = {c for c in candidates if c in self.kg.entity_to_id}
        print(f"{candidates=}")
        if len(candidates) == 1:
            return list(candidates)[0]
        if len(candidates) == 0:
            return None

        # 2. select the most likely candidate given the context
        with dspy.context(lm=self.lm):
            entity = self.candidates_selector(
                entity_candidates=candidates, context=context
            ).entity
        if not entity in self.kg.entity_to_id:
            return None
        return entity

    def fuzzy_link_relation(self, relation: str) -> Optional[str]:
        assert not self.relation_picker is None
        assert not self.lm is None

        if relation in self.kg.rel_to_id:
            return relation

        with dspy.context(lm=self.lm):
            normalized_relation = self.relation_picker(
                candidate_relation=relation,
                possible_relations=list(self.kg.rel_to_id.keys()),
            ).relation
        if not normalized_relation in self.kg.rel_to_id:
            return None
        return normalized_relation

    def fuzzy_link_triplet(
        self, subject: str, relation: str, object: str, context: str
    ) -> tuple[str | None, str | None, str | None]:
        resolved_subject = (
            "*" if subject == "*" else self.fuzzy_link_entity(subject, context)
        )
        resolved_relation = (
            "*" if relation == "*" else self.fuzzy_link_relation(relation)
        )
        resolved_object = (
            "*" if object == "*" else self.fuzzy_link_entity(object, context)
        )
        return (resolved_subject, resolved_relation, resolved_object)

    def oracle_link_entity(
        self, entity: str, events: list[str], entity_type: Literal["subject", "object"]
    ) -> str | None:
        SIM_THRESHOLD = 50.0  # low bar to pass to consider a match

        # events are in TKGQA format: subj|rel|obj|start|end
        evts = [evt.split("|") for evt in events]
        if entity_type == "subject":
            event_entities = {subj for subj, *_ in evts}
        elif entity_type == "object":
            event_entities = {obj for _, _, obj, *_ in evts}
        else:
            raise ValueError(entity_type)
        if len(event_entities) == 0:
            return entity if entity in self.kg.entity_to_id else None

        sim = {candidate: fuzz.ratio(entity, candidate) for candidate in event_entities}
        closest_entity = max(event_entities, key=sim.get)  # type: ignore
        if sim[closest_entity] < SIM_THRESHOLD:
            return entity if entity in self.kg.entity_to_id else None
        return closest_entity

    def oracle_link_relation(self, relation: str, events: list[str]) -> str | None:
        SIM_THRESHOLD = 50.0  # low bar to pass to consider a match

        # events are in TKGQA format: subj|rel|obj|start|end
        evts = [evt.split("|") for evt in events]
        event_relations = {rel for _, rel, *_ in evts}
        if len(event_relations) == 0:
            return relation if relation in self.kg.rel_to_id else None

        sim = {
            candidate: fuzz.ratio(candidate, relation) for candidate in event_relations
        }
        closest_relation = max(event_relations, key=sim.get)  # type: ignore
        if sim[closest_relation] < SIM_THRESHOLD:
            return relation if relation in self.kg.rel_to_id else None
        return closest_relation

    def oracle_link_triplet(
        self, subject: str, relation: str, object: str, events: list[str]
    ) -> tuple[str | None, str | None, str | None]:
        resolved_subject = (
            "*"
            if subject == "*"
            else self.oracle_link_entity(subject, events, "subject")
        )
        resolved_relation = (
            "*" if relation == "*" else self.oracle_link_relation(relation, events)
        )
        resolved_object = (
            "*" if object == "*" else self.oracle_link_entity(object, events, "object")
        )
        return (resolved_subject, resolved_relation, resolved_object)

    def link_triplet(
        self,
        subject: str,
        relation: str,
        object: str,
        context: str | None = None,
        events: list[str] | None = None,
    ) -> tuple[tuple[str, str, str] | None, str | None]:
        """
        :param context: must be supplied if linking_style is 'fuzzy'
        :param events: must be supplied if linking_style is 'oracle'

        :return: ((subj, rel, obj) | None, error | None)
        """
        if self.linking_style == "exact":
            return (subject, relation, object), None

        elif self.linking_style in {"fuzzy", "oracle"}:
            if self.linking_style == "fuzzy":
                assert not context is None
                linked_subject, linked_relation, linked_object = (
                    self.fuzzy_link_triplet(subject, relation, object, context)
                )
            elif self.linking_style == "oracle":
                assert not events is None
                linked_subject, linked_relation, linked_object = (
                    self.oracle_link_triplet(subject, relation, object, events)
                )
            else:
                raise ValueError(self.linking_style)

            linking_errors = []
            if linked_subject is None:
                linking_errors.append(f"{subject} is not in knowledge base.")
            if linked_relation is None:
                linking_errors.append(f"{relation} is not in knowledge base.")
            if linked_object is None:
                linking_errors.append(f"{object} is not in knowledge base.")
            if len(linking_errors) > 0:
                return None, "Error: " + " ".join(linking_errors)

            assert not linked_subject is None
            assert not linked_relation is None
            assert not linked_object is None
            return (linked_subject, linked_relation, linked_object), None

        else:
            raise ValueError(f"unknown linking style: {self.linking_style}")

    def __call__(
        self,
        subject: str,
        relation: str,
        object: str,
        start: str,
        end: str,
        context: str | None = None,
        events: list[str] | None = None,
    ) -> str:
        """
        :param context: must be supplied if linking_style is 'fuzzy'
        :param events: must be supplied if linking_style is 'oracle'
        """
        if not isinstance(subject, str):
            return f"Incorrect subject input: {subject}"
        if not isinstance(relation, str):
            return f"Incorrect relation input: {relation}"
        if not isinstance(object, str):
            return f"Incorrect input: {object}"
        if not isinstance(start, str):
            return f"Incorrect input: {start}"
        if not isinstance(end, str):
            return f"Incorrect input: {end}"
        if not start == "beginning of time" and not re.match(
            r"[0-9]{4}-[0-9]{2}-[0-9]{2}", start
        ):
            return f"Incorrect input format for 'start': {start} (should be YYYY-MM-DD or 'beginning of time')."
        if not end == "end of time" and not re.match(
            r"[0-9]{4}-[0-9]{2}-[0-9]{2}", end
        ):
            return f"Incorrect input format for 'end': {end} (should be YYYY-MM-DD or 'end of time')."

        maybe_linked_triplet, maybe_err = self.link_triplet(
            subject, relation, object, context, events
        )
        if maybe_err:
            return maybe_err
        assert not maybe_linked_triplet is None
        linked_subject, linked_relation, linked_object = maybe_linked_triplet

        try:
            matches = retrieve_with_constraints(
                self.kg, linked_subject, linked_relation, linked_object, (start, end)
            )
        except KeyError as e:
            return f"Error: {e} is not in the knowledge base."
        except Exception as e:
            return f"Error: {repr(e)}"
        if len(matches) == 0:
            return "No quadruple match the request."

        if len(matches) > 32:
            matches = matches[:32]
            return (
                "\n".join([str(m) for m in matches])
                + "\n... the rest of the content has been truncated (too many matches)."
            )
        return "\n".join([str(m) for m in matches])

    def get_tool_abstract_fn(self) -> Callable[[str, str, str, str, str], str]:
        def query_knowledge_base(
            subject: str, relation: str, object: str, start: str, end: str
        ) -> str:
            """Query the temporal knowledge base.

            Args:
                subject: Searched subject.  '*' indicates any subject.
                relation: Searched relation.  '*' indicates any relation.
                object: Searched object.  '*' indicates any object.
                start: earliest accepted timestamp, in YYYY-MM-DD format. The special value 'beginning of time' is allowed.
                end: Latest accepted timestamp, in YYYY-MM-DD format.  The special value 'end of time' is allowed.

            Returns:
                a list of matching temporal facts, as quadruples of the form (subject, relation, object, (start, end)).
            """
            raise NotImplementedError

        return query_knowledge_base

    def get_tool_dict(self) -> dict:
        return get_tool_dict(self.get_tool_abstract_fn())
