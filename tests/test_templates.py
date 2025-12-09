import pytest
from hypothesis import given, strategies as st
import pandas as pd
from TimelineKGQA.templates import get_paraphrase_examples

st_allen_relation = st.one_of(
    *[
        st.just(f"X {op} Y")
        for op in [
            "<",
            ">",
            "m",
            "mi",
            "o",
            "oi",
            "s",
            "si",
            "d",
            "di",
            "f",
            "fi",
            "=",
        ]
    ]
)


@given(
    st.one_of(st.just("subject"), st.just("object")),
    st.tuples(st_allen_relation, st_allen_relation),
)
def test_get_paraphrase_examples_allen_combination(
    answer_type: str, allen_relation: tuple[str, str]
):
    allen1, allen2 = allen_relation
    examples = get_paraphrase_examples(
        {
            "question_level": "complex",
            "question_type": "timeline_position_retrieval*2+temporal_constrained_retrieval",
            "answer_type": answer_type,
            "temporal_relation": f"{allen1}&{allen2}",
        }
    )
    assert len(examples) <= 2


MEDIUM_TPR_TCR_SUBJ_QUESTION_PARAMS = [
    (
        "medium",
        "timeline_position_retrieval_temporal_constrained_retrieval",
        "subject",
        temporal_relation,
    )
    for temporal_relation in [
        "X < Y",
        "X > Y",
        "X m Y",
        "X mi Y",
        "X o Y",
        "X oi Y",
        "X d Y",
        "X di Y",
        "X s Y",
        "X si Y",
        "X f Y",
        "X fi Y",
        "X = Y",
        "duration_before",
        "duration_after",
    ]
]

MEDIUM_TPR_TCR_OBJ_QUESTION_PARAMS = [
    (question_level, question_type, "object", temporal_relation)
    for question_level, question_type, _, temporal_relation in MEDIUM_TPR_TCR_SUBJ_QUESTION_PARAMS
]


@pytest.mark.parametrize(
    "question_level,question_type,answer_type,temporal_relation",
    [
        ("simple", "temporal_constrained_retrieval", "subject", None),
        ("simple", "temporal_constrained_retrieval", "object", None),
        ("simple", "timeline_position_retrieval", "timestamp_start", None),
        ("simple", "timeline_position_retrieval", "timestamp_end", None),
        ("simple", "timeline_position_retrieval", "timestamp_range", None),
        ("simple", "timeline_position_retrieval", "duration", None),
    ]
    + MEDIUM_TPR_TCR_SUBJ_QUESTION_PARAMS
    + MEDIUM_TPR_TCR_OBJ_QUESTION_PARAMS,
)
def test_get_paraphrase_examples_no_combination(
    question_level: str,
    question_type: str,
    answer_type: str,
    temporal_relation: str | None,
):
    examples = get_paraphrase_examples(
        {
            "question_level": question_level,
            "question_type": question_type,
            "answer_type": answer_type,
            "temporal_relation": temporal_relation,
        }
    )
    assert len(examples) == 1


@pytest.mark.parametrize(
    "temporal_relation",
    [
        ("duration_3883 days before&duration_starts"),
        ("duration_3883 days after&duration_startedby"),
        ("duration_during&duration_2348 days before"),
        ("duration_overlaps&duration_2348 days before"),
        ("duration_finishes&duration_1713 days after"),
        ("duration_finishedby&duration_1713 days after"),
    ],
)
def test_get_paraphrase_complex_duration(temporal_relation: str):
    for answer_type in ["subject", "object"]:
        examples = get_paraphrase_examples(
            {
                "question_level": "complex",
                "question_type": "timeline_position_retrieval*2+temporal_constrained_retrieval",
                "answer_type": answer_type,
                "temporal_relation": temporal_relation,
            }
        )
        assert len(examples) == 2
