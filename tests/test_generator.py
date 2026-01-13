import pandas as pd
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


def test_medium_subjects_matching_allen():
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
    assert generator.medium_subjects_matching_allen(
        "p1", "o1", "X < Y", "2030", "2031"
    ) == {"s1", "s2"}


def test_medium_objects_matching_allen():
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
    assert generator.medium_objects_matching_allen(
        "s1", "p1", "X < Y", "2030", "2031"
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
        "p1", "o1", "X oi Y", "2020", "2022", 
                    "X < Y" , "2030", "2031"
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
        "s1", "p1", "X oi Y", "2020", "2022", 
                    "X < Y" , "2030", "2031"
    ) == {"o1"}
    # fmt: on


def test_medium_subjects_matching_durationorallen_allen():
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
    assert generator.medium_subjects_matching_duration_or_allen(
        "p1", "o1", None, None, None, "X < Y", "2030", "2031"
    ) == {"s1", "s2"}


def test_medium_subjects_matching_durationorallen_duration():
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
    assert generator.medium_subjects_matching_duration_or_allen(
        "p1",
        "o1",
        "before",
        "duration_before",
        timedelta(days=365),
        None,
        second_start,
        second_end,
    ) == {"s1"}
