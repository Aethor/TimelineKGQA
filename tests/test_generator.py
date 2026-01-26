from gradio.utils import assert_configs_are_equivalent_besides_ids
from typing import Literal
import pandas as pd
from hypothesis import given, settings, strategies as st
from datetime import timedelta
from TimelineKGQA.generator import TKGQAGenerator


def test_simple_subjects_matching():
    generator = TKGQAGenerator.__new__(TKGQAGenerator)
    # fmt: off
    generator.events_df = pd.DataFrame(
        {
            "subject":    ["s1",  "s2",  "s3"],
            "predicate":  ["p1",  "p1",  "p2"],
            "object":     ["o1",  "o1",  "o2"],
            "start_time": ["st1", "st1", "st2"],
            "end_time":   ["et1", "et1", "et2"],
        }
    )
    # fmt: off
    assert generator.simple_subjects_matching("p1", "o1", "st1", "et1") == {"s1", "s2"}


def test_simple_objects_matching():
    generator = TKGQAGenerator.__new__(TKGQAGenerator)
    # fmt: off
    generator.events_df = pd.DataFrame(
        {
            "subject":    ["s1",  "s1",  "s3"],
            "predicate":  ["p1",  "p1",  "p2"],
            "object":     ["o1",  "o2",  "o3"],
            "start_time": ["st1", "st1", "st2"],
            "end_time":   ["et1", "et1", "et2"],
        }
    )
    # fmt: on
    assert generator.simple_objects_matching("s1", "p1", "st1", "et1") == {"o1", "o2"}


def test_simple_timestamp_range_matching():
    generator = TKGQAGenerator.__new__(TKGQAGenerator)
    # fmt: off
    generator.events_df = pd.DataFrame(
        {
            "subject":    ["s1",  "s1",  "s2"],
            "predicate":  ["p1",  "p1",  "p2"],
            "object":     ["o1",  "o1",  "o2"],
            "start_time": ["st1", "st2", "st3"],
            "end_time":   ["et1", "et2", "et3"],
        }
    )
    # fmt: on
    assert generator.simple_timestamp_range_matching("s1", "p1", "o1") == {
        ("st1", "et1"),
        ("st2", "et2"),
    }


def test_medium_subjects_matching_timerange_relation_property():
    generator = TKGQAGenerator.__new__(TKGQAGenerator)
    # fmt: off
    generator.events_df = pd.DataFrame(
        {
            "subject":    ["s1",   "s2",   "s3"],
            "predicate":  ["p1",   "p1",   "p1"],
            "object":     ["o1",   "o1",   "o1"],
            "start_time": ["2022", "2012", "2032"],
            "end_time":   ["2023", "2013", "2033"],
        }
    )
    # fmt: on
    assert generator.medium_subjects_matching_timerange_relation_property(
        "p1", "o1", "before", "2030", "2031"
    ) == {"s1", "s2"}


def test_medium_objects_matching_timerange_relation_property():
    generator = TKGQAGenerator.__new__(TKGQAGenerator)
    # fmt: off
    generator.events_df = pd.DataFrame(
        {
            "subject":    ["s1",   "s1",   "s1"],
            "predicate":  ["p1",   "p1",   "p1"],
            "object":     ["o1",   "o2",   "o3"],
            "start_time": ["2022", "2012", "2032"],
            "end_time":   ["2023", "2013", "2033"],
        }
    )
    # fmt: on
    assert generator.medium_objects_matching_timerange_relation_property(
        "s1", "p1", "before", "2030", "2031"
    ) == {"o1", "o2"}


def test_medium_subjects_matching_duration():
    generator = TKGQAGenerator.__new__(TKGQAGenerator)
    # fmt: off
    generator.events_df = pd.DataFrame(
        {
            "subject":    ["s1",   "s2",   "s3"],
            "predicate":  ["p1",   "p1",   "p2"],
            "object":     ["o1",   "o1",   "o2"],
            "start_time": ["2021", "2023", "2032"],
            "end_time":   ["2022", "2024", "2033"],
        }
    )
    # fmt: on
    second_start, second_end = TKGQAGenerator.utils_time_range_str_to_datetime(
        ["2023", "2024"]
    )
    assert generator.medium_subjects_matching_duration(
        "p1", "o1", "duration_before", timedelta(days=365), second_start, second_end
    ) == {"s1"}


def test_intervals_matching_intersection():
    generator = TKGQAGenerator.__new__(TKGQAGenerator)
    # fmt: off
    generator.events_df = pd.DataFrame(
        {
            "subject":    ["s1",   "s2",  "s1",    "s2",   "s3"],
            "predicate":  ["p1",   "p2",  "p1",    "p2",   "p3"],
            "object":     ["o1",   "o2",  "o1",    "o2",   "o3"],
            "start_time": ["2021", "2020", "2018", "2019", "2030"],
            "end_time":   ["2023", "2022", "2020", "2020", "2031"],
        }
    )
    # fmt: on
    assert generator.intervals_matching_intersection(
        ["s1", "s2"], ["p1", "p2"], ["o1", "o2"]
    ) == {("2021", "2022"), ("2019", "2020")}


def test_complex_subjects_matching():
    generator = TKGQAGenerator.__new__(TKGQAGenerator)
    # fmt: off
    generator.events_df = pd.DataFrame(
        {
            "subject":    ["s1",   "s2",  "s1",    "s2",   "s3"],
            "predicate":  ["p1",   "p2",  "p1",    "p2",   "p3"],
            "object":     ["o1",   "o2",  "o1",    "o2",   "o3"],
            "start_time": ["2021", "2020", "2018", "2019", "2030"],
            "end_time":   ["2023", "2022", "2020", "2020", "2031"],
        }
    )
    assert generator.complex_subjects_matching(
        "p1", "o1", "during", "2020", "2022", 
                    "before", "2030", "2031"
    ) == {"s1"}
    # fmt: on


def test_complex_objects_matching():
    generator = TKGQAGenerator.__new__(TKGQAGenerator)
    # fmt: off
    generator.events_df = pd.DataFrame(
        {
            "subject":    ["s1",   "s2",  "s1",    "s2",   "s3"],
            "predicate":  ["p1",   "p2",  "p1",    "p2",   "p3"],
            "object":     ["o1",   "o2",  "o1",    "o2",   "o3"],
            "start_time": ["2021", "2020", "2018", "2019", "2030"],
            "end_time":   ["2023", "2022", "2020", "2020", "2031"],
        }
    )
    assert generator.complex_objects_matching(
        "s1", "p1", "during", "2020", "2022", 
                    "before", "2030", "2031"
    ) == {"o1"}
    # fmt: on


def test_medium_subjects_matching_duration_or_tpr__timerange_relation_property():
    generator = TKGQAGenerator.__new__(TKGQAGenerator)
    # fmt: off
    generator.events_df = pd.DataFrame(
        {
            "subject":    ["s1",   "s2",   "s3"],
            "predicate":  ["p1",   "p1",   "p1"],
            "object":     ["o1",   "o1",   "o1"],
            "start_time": ["2022", "2012", "2032"],
            "end_time":   ["2023", "2013", "2033"],
        }
    )
    # fmt: on
    assert generator.medium_subjects_matching_duration_or_timerange_relation_property(
        "p1", "o1", None, None, None, "before", "2030", "2031"
    ) == {"s1", "s2"}


def test_medium_subjects_matching_duration_or_tpr__duration():
    generator = TKGQAGenerator.__new__(TKGQAGenerator)
    # fmt: off
    generator.events_df = pd.DataFrame(
        {
            "subject":    ["s1",   "s2",   "s3"],
            "predicate":  ["p1",   "p1",   "p2"],
            "object":     ["o1",   "o1",   "o2"],
            "start_time": ["2021", "2023", "2032"],
            "end_time":   ["2022", "2024", "2033"],
        }
    )
    # fmt: on
    second_start, second_end = TKGQAGenerator.utils_time_range_str_to_datetime(
        ["2023", "2024"]
    )
    assert generator.medium_subjects_matching_duration_or_timerange_relation_property(
        "p1",
        "o1",
        "before",
        "duration_before",
        timedelta(days=365),
        None,
        second_start,
        second_end,
    ) == {"s1"}


st_ascii = st.text(st.characters(codec="ascii"))


@st.composite
def st_timerange(draw):
    start_time = draw(st.dates())
    end_time = draw(st.dates(min_value=start_time))
    return (start_time, end_time)


@st.composite
def st_event_dfs(draw, max_size: int = 128):
    df_len = draw(st.integers(min_value=1, max_value=max_size))
    timeranges = draw(st.lists(st_timerange(), min_size=df_len, max_size=df_len))
    return pd.DataFrame(
        {
            "subject": draw(st.lists(st_ascii, min_size=df_len, max_size=df_len)),
            "predicate": draw(st.lists(st_ascii, min_size=df_len, max_size=df_len)),
            "object": draw(st.lists(st_ascii, min_size=df_len, max_size=df_len)),
            "start_time": [str(start) for start, _ in timeranges],
            "end_time": [str(end) for _, end in timeranges],
        }
    )


@st.composite
def st_event_dicts(draw):
    start, end = draw(st_timerange())
    return {
        "subject": draw(st_ascii),
        "predicate": draw(st_ascii),
        "object": draw(st_ascii),
        "start_time": str(start),
        "end_time": str(end),
    }


@given(st_event_dicts(), st_event_dfs())
def test_simple_question_generation_individual(event: dict, events_df: pd.DataFrame):
    generator = TKGQAGenerator.__new__(TKGQAGenerator)
    generator.events_df = events_df
    questions = generator.simple_question_generation_individual(
        event["subject"],
        event["predicate"],
        event["object"],
        event["start_time"],
        event["end_time"],
    )
    assert len(questions) > 0


@given(st_event_dicts(), st_event_dicts(), st_event_dfs())
def test_medium_question_generation_individual(
    event1: dict, event2: dict, events_df: pd.DataFrame
):
    generator = TKGQAGenerator.__new__(TKGQAGenerator)
    generator.events_df = events_df
    questions = generator.medium_question_generation_individual(event1, event2)
    assert len(questions) > 0


@given(st_event_dicts(), st_event_dicts(), st_event_dicts(), st_event_dfs())
def test_complex_question_generation_individual(
    event1: dict, event2: dict, event3: dict, events_df: pd.DataFrame
):
    generator = TKGQAGenerator.__new__(TKGQAGenerator)
    generator.events_df = events_df
    questions = generator.complex_question_generation_individual(event1, event2, event3)
    assert len(questions) > 0
