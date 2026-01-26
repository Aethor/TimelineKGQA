import pytest
from hypothesis import given, assume, strategies as st
import pandas as pd
from TimelineKGQA.generator import TKGQAGenerator
from TimelineKGQA.templates import get_paraphrase_examples


st_timerange_relation_property = st.one_of(
    st.just("start=start"),
    st.just("end=end"),
    st.just("start=end"),
    st.just("end=start"),
    st.just("start<start"),
    st.just("end<end"),
    st.just("start<end"),
    st.just("end<start"),
    st.just("start>start"),
    st.just("end>end"),
    st.just("start>end"),
    st.just("end>start"),
    st.just("before"),
    st.just("after"),
    st.just("during"),
)


@given(
    st.one_of(st.just("subject"), st.just("object")),
    st_timerange_relation_property,
    st_timerange_relation_property,
)
def test_get_paraphrase_examples_timerange_relation_properties_combination(
    answer_type: str, tpr1: str, tpr2: str
):
    assume(TKGQAGenerator.are_timerange_relation_properties_compatible(tpr1, tpr2))
    examples = get_paraphrase_examples(
        {
            "question_level": "complex",
            "question_type": "timeline_position_retrieval*2+temporal_constrained_retrieval",
            "answer_type": answer_type,
            "temporal_relation": f"{tpr1}&{tpr2}",
        }
    )
    assert len(examples) <= 2


MEDIUM_TPR_TCR_SUBJ_QUESTION_PARAMS = [
    (
        "medium",
        "timeline_position_retrieval_temporal_constrained_retrieval",
        "subject",
        temporal_relation_property,
    )
    for temporal_relation_property in [
        "start=start",
        "end=end",
        "start=end",
        "end=start",
        "start<start",
        "end<end",
        "start<end",
        "end<start",
        "start>start",
        "end>end",
        "start>end",
        "end>start",
        "before",
        "after",
        "during",
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
        ("duration_3883 days before&duration_start=end"),
        ("duration_3883 days after&duration_start<end"),
        ("duration_3883 days after&duration_before"),
        ("duration_during&duration_2348 days before"),
        ("duration_start=start&duration_2348 days before"),
        ("duration_start<end&duration_1713 days after"),
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
