from typing import Mapping
import re

# noqa: E501
QUESTION_TEMPLATES = {
    "simple": {
        "temporal_constrained_retrieval": {
            "subject": [
                "Who {predicate} {tail_object} from {start_time} to {end_time}?",
                "{tail_object} is {predicate} by who from {start_time} to {end_time}?",
            ],
            "object": [
                "{subject} {predicate} which organisation/what/who from {start_time} to {end_time}?",
                "Which organisation is {predicate} by {subject} from {start_time} to {end_time}?",
            ],
        },
        "timeline_position_retrieval": {
            "timestamp_start": [
                "When did {subject} {predicate} {tail_object} start?",
                "At what time did {subject} start {predicate} {tail_object}?",
            ],
            "timestamp_end": [
                "When did {subject} end {predicate} {tail_object}?",
                "At what time did {subject} finish {predicate} {tail_object}?",
            ],
            "timestamp_range": [
                "From when to when did {subject} {predicate} {tail_object}?",
                "During what time {subject} {predicate} {tail_object}?",
            ],
            "duration": [
                "How long did {subject} {predicate} {tail_object}?",
                "What is the duration of {subject} {predicate} {tail_object}?",
            ],
        },
    },
    "medium": {
        "timeline_position_retrieval_temporal_constrained_retrieval": {
            "subject": {
                "before": [
                    "Who/Which organisation {first_event_predicate} {first_event_object} before {second_event_subject} {second_event_predicate} {second_event_object}?",
                    "Before {second_event_subject} {second_event_predicate} {second_event_object}, Who/Which organisation {first_event_predicate} {first_event_object}?",
                    "Earlier than {second_event_subject} {second_event_predicate} {second_event_object}, Who/Which organisation {first_event_predicate} {first_event_object}?",
                    "Prior to {second_event_subject} {second_event_predicate} {second_event_object}, Who/Which organisation {first_event_predicate} {first_event_object}?",
                    "Who/Which Organisation {first_event_predicate} {first_event_object} ahead of {second_event_subject} {second_event_predicate} {second_event_object}?",
                    "Who/Which organisation {first_event_predicate} {first_event_object} preceding {second_event_subject} {second_event_predicate} {second_event_object}?",
                    "Who/Which organisation {first_event_predicate} {first_event_object} earlier than {second_event_subject} {second_event_predicate} {second_event_object}?",
                    "Who/Which organisation {first_event_predicate} {first_event_object} in advance of {second_event_subject} {second_event_predicate} {second_event_object}?",
                ],
                "after": [
                    "Who/Which organisation {first_event_predicate} {first_event_object} after {second_event_subject} {second_event_predicate} {second_event_object}?",
                    "After {second_event_subject} {second_event_predicate} {second_event_object}, who/which organisation {first_event_predicate} {first_event_object}?",
                ],
                "during": [
                    "Who/which organisation {first_event_predicate} {first_event_object} during {second_event_subject} {second_event_predicate} {second_event_object}?",
                    "During {second_event_subject} {second_event_predicate} {second_event_object}, who/which organisation {first_event_predicate} {first_event_object}?",
                    "Who/Which organisation {first_event_predicate} {first_event_object} while {second_event_subject} {second_event_predicate} {second_event_object}?",
                    "While {second_event_subject} {second_event_predicate} {second_event_object}, who/which organisation {first_event_predicate} {first_event_object}?",
                    "In the midst of {second_event_subject} {second_event_predicate} {second_event_object}, who/which organisation {first_event_predicate} {first_event_object}?",
                ],
                "start=start": [
                    "Who/which organisation starts {first_event_predicate} {first_event_object}, at the same time {second_event_subject} start {second_event_predicate} {second_event_object}?",
                    "At the same time {second_event_subject} start {second_event_predicate} {second_event_object}, who/which organisation starts {first_event_predicate} {first_event_object}?",
                ],
                "end=end": [
                    "Who/Which organisation finishes {first_event_predicate} {first_event_object}, at the same time {second_event_subject} finish {second_event_predicate} {second_event_object}?",
                    "At the same time {second_event_subject} finish {second_event_predicate} {second_event_object}, who/which organisation finishes {first_event_predicate} {first_event_object}?",
                ],
                "start=end": [
                    "When {second_event_subject} ends {second_event_predicate} {second_event_object}, who/which organisation starts {first_event_predicate} {first_event_object}?",
                    "Who/which organisation starts {first_event_predicate} {first_event_object} when {second_event_subject} ends {second_event_predicate} {second_event_object}?",
                ],
                "end=start": [
                    "When {second_event_subject} starts {second_event_predicate} {second_event_object}, who/which organisation ends {first_event_predicate} {first_event_object}?",
                    "Who/which organisation ends {first_event_predicate} {first_event_object} when {second_event_subject} starts {second_event_predicate} {second_event_object}?",
                ],
                "start<start": [
                    "Who/which organisation starts {first_event_predicate} {first_event_object} before {second_event_subject} starts {second_event_predicate} {second_event_object}?",
                    "Before {second_event_subject} starts {second_event_predicate} {second_event_object}, who/which organisation starts {first_event_predicate} {first_event_object}?",
                ],
                "start>start": [
                    "Who/which organisation starts {first_event_predicate} {first_event_object} after {second_event_subject} starts {second_event_predicate} {second_event_object}?",
                    "After {second_event_subject} starts {second_event_predicate} {second_event_object}, who/which organisation starts {first_event_predicate} {first_event_object}?",
                ],
                "end<end": [
                    "Who/which organisation ends {first_event_predicate} {first_event_object} before {second_event_subject} ends {second_event_predicate} {second_event_object}?",
                    "Before {second_event_subject} ends {second_event_predicate} {second_event_object}, who/which organisation ends {first_event_predicate} {first_event_object}?",
                ],
                "end>end": [
                    "Who/which organisation ends {first_event_predicate} {first_event_object} after {second_event_subject} ends {second_event_predicate} {second_event_object}?",
                    "After {second_event_subject} ends {second_event_predicate} {second_event_object}, who/which organisation ends {first_event_predicate} {first_event_object}?",
                ],
                "start<end": [
                    "Who/which organisation starts {first_event_predicate} {first_event_object} before {second_event_subject} ends {second_event_predicate} {second_event_object}?",
                    "Before {second_event_subject} ends {second_event_predicate} {second_event_object}, who/which organisation starts {first_event_predicate} {first_event_object}?",
                ],
                "start>end": [
                    "Who/which organisation starts {first_event_predicate} {first_event_object} after {second_event_subject} ends {second_event_predicate} {second_event_object}?",
                    "After {second_event_subject} ends {second_event_predicate} {second_event_object}, who/which organisation starts {first_event_predicate} {first_event_object}?",
                ],
                "end<start": [
                    "Who/which organisation ends {first_event_predicate} {first_event_object} before {second_event_subject} starts {second_event_predicate} {second_event_object}?",
                    "Before {second_event_subject} starts {second_event_predicate} {second_event_object}, who/which organisation ends {first_event_predicate} {first_event_object}?",
                ],
                "end>start": [
                    "Who/which organisation ends {first_event_predicate} {first_event_object} after {second_event_subject} starts {second_event_predicate} {second_event_object}?",
                    "After {second_event_subject} starts {second_event_predicate} {second_event_object}, who/which organisation ends {first_event_predicate} {first_event_object}?",
                ],
                "duration_before": [
                    "Who {first_event_predicate} {first_event_object} {temporal_relation} {second_event_subject} {second_event_predicate} {second_event_object}?",
                ],
                "duration_after": [
                    "Who {first_event_predicate} {first_event_object} {temporal_relation} {second_event_subject} {second_event_predicate} {second_event_object}?",
                ],
            },
            "object": {
                "before": [
                    "Before {second_event_subject} {second_event_predicate} {second_event_object}, who/what/which organisation is {first_event_predicate} by {first_event_subject}?",
                    "Who/What/Which organisation is {first_event_predicate}ed by {first_event_subject} before {second_event_subject} {second_event_predicate} {second_event_object}?",
                ],
                "after": [
                    "{first_event_subject} {first_event_predicate} who/what/which organisation after {second_event_subject} {second_event_predicate} {second_event_object}?",
                    "Who/What/Which organisation is {first_event_predicate}ed by {first_event_subject} after {second_event_subject} {second_event_predicate} {second_event_object}?",
                ],
                "during": [
                    "During {second_event_subject} {second_event_predicate} {second_event_object}, who/what/which organisation is {first_event_predicate}ed by {first_event_subject}?",
                    "Who/What/Which organisation is {first_event_predicate}ed {first_event_subject} while {second_event_subject} {second_event_predicate} {second_event_object}?",
                    "Who/What/Which organisation is {first_event_predicate}ed {first_event_subject} during the period when {second_event_subject} {second_event_predicate} {second_event_object}?",
                    "While {second_event_subject} {second_event_predicate} {second_event_object}, who/what/which organisation is {first_event_predicate}ed {first_event_subject}?",
                ],
                "start=start": [
                    "At the same time {second_event_subject} start {second_event_predicate} {second_event_object}, in which organisation/what/who {first_event_subject} starts {first_event_predicate}?",
                ],
                "end=end": [
                    "At the same time {second_event_subject} finish {second_event_predicate} {second_event_object}, in which organisation/what/who {first_event_subject} finishes {first_event_predicate}?",
                ],
                "start=end": [
                    "{second_event_subject} ends {second_event_predicate} {second_event_object} at the same time {first_event_subject} starts {first_event_predicate} with who/what/which organisation?",
                ],
                "end=start": [
                    "{second_event_subject} starts {second_event_predicate} {second_event_object} at the same time {first_event_subject} ends {first_event_predicate} with who/what/which organisation?",
                ],
                "start<start": [
                    "Before {second_event_subject} starts {second_event_predicate} {second_event_object}, {first_event_subject} starts {first_event_predicate} with who/what/which organisation?",
                ],
                "start>start": [
                    "After {second_event_subject} starts {second_event_predicate} {second_event_object} {first_event_subject} starts {first_event_predicate} with who/what/which organisation?",
                ],
                "end<end": [
                    "Before {second_event_subject} ends {second_event_predicate} {second_event_object} {first_event_subject} ends {first_event_predicate} with who/what/which organisation?",
                ],
                "end>end": [
                    "After {second_event_subject} ends {second_event_predicate} {second_event_object} {first_event_subject} ends {first_event_predicate} with who/what/which organisation?",
                ],
                "start<end": [
                    "Before {second_event_subject} ends {second_event_predicate} {second_event_object} {first_event_subject} starts {first_event_predicate} with who/what/which organisation?",
                ],
                "start>end": [
                    "After {second_event_subject} ends {second_event_predicate} {second_event_object} {first_event_subject} starts {first_event_predicate} with who/what/which organisation?",
                ],
                "end<start": [
                    "Before {second_event_subject} starts {second_event_predicate} {second_event_object} {first_event_subject} starts {first_event_predicate} with who/what/which organisation?",
                ],
                "end>start": [
                    "After {second_event_subject} starts {second_event_predicate} {second_event_object} {first_event_subject} ends {first_event_predicate} with who/what/which organisation?",
                ],
                "duration_before": [
                    "{temporal_relation} {second_event_subject} {second_event_predicate} {second_event_object}, in which organisation/what/who {first_event_subject} {first_event_predicate}?",
                ],
                "duration_after": [
                    "{temporal_relation} {first_event_subject} {first_event_predicate} {first_event_object}, in which organisation/what/who {first_event_subject} {first_event_predicate}?",
                ],
            },
        },
        "timeline_position_retrieval_timeline_position_retrieval": {
            # because it is the time range, then we should also ask about the duration
            "timestamp_range": {
                "intersection": [
                    "From when to when, {first_event_subject} {first_event_predicate} {first_event_object}, at the same time, {second_event_subject} {second_event_predicate} {second_event_object}?"
                ],
            },
            # we are looking for the allen temporal relation between the two events, so the question normally is asked for relation directly, or true/false question.
            # However, it is still possible to have specific format for specific relationship question, even it is true/false question.
            # We will do choice and random for now, consider this later.
            "relation_allen": {
                "relation_allen": [
                    "What's the Allen temporal relation between {first_event_subject} {first_event_predicate} {first_event_object} and {second_event_subject} {second_event_predicate} {second_event_object}?",
                ],
            },
            "relation_duration": {
                # duration for the intersection of the two events
                "duration": [
                    "What is the duration of {first_event_subject} {first_event_predicate} {first_event_object} jointly when {second_event_subject} {second_event_predicate} {second_event_object}?",
                ],
                "duration_compare": [
                    "Is the duration of {first_event_subject} {first_event_predicate} {first_event_object} {temporal_relation} the duration of {second_event_subject} {second_event_predicate} {second_event_object}?",
                ],
                # This is actually for union
                "sum": [
                    "How long is the total duration of {first_event_subject} {first_event_predicate} {first_event_object} and {second_event_subject} {second_event_predicate} {second_event_object}?",
                ],
                "average": [
                    "What is the average duration of {first_event_subject} {first_event_predicate} {first_event_object} and {second_event_subject} {second_event_predicate} {second_event_object}?",
                ],
            },
        },
    },
    "complex": {
        "timeline_position_retrieval*2+temporal_constrained_retrieval": {
            # we can use two kinds of conditions in these types of
            # questions: either interval based or interval bounds
            # based.
            "subject": {
                "interval": [
                    "Who {first_event_predicate} {first_event_object}, {temporal_relation_12} {second_event_subject} {second_event_predicate} {second_event_object}, {temporal_relation_13} {third_event_subject} {third_event_predicate} {third_event_object}?",
                ],
                "bound": [
                    "Who {first_event_temporal_bound} {first_event_predicate} {first_event_object}, {temporal_relation_12} {second_event_subject} {second_event_temporal_bound} {second_event_predicate} {second_event_object}, {temporal_relation_13} {third_event_subject} {third_event_temporal_bound} {third_event_predicate} {third_event_object}?",
                ],
            },
            "object": {
                "interval": [
                    "{first_event_subject} {first_event_predicate} which organisation/what/who, {temporal_relation_12} {second_event_subject} {second_event_predicate} {second_event_object}, {temporal_relation_13} {third_event_subject} {third_event_predicate} {third_event_object}?",
                ],
                "bound": [
                    "{first_event_subject} {first_event_temporal_bound} {first_event_predicate} which organisation/what/who, {temporal_relation_12} {second_event_subject} {second_event_temporal_bound} {second_event_predicate} {second_event_object}, {temporal_relation_13} {third_event_subject} {third_event_temporal_bound} {third_event_predicate} {third_event_object}?",
                ],
            },
        },
        "timeline_position_retrieval*3": {
            "timestamp_range": {
                "intersection": [
                    "From when to when, {first_event_subject} {first_event_predicate} {first_event_object}, at the same time, {second_event_subject} {second_event_predicate} {second_event_object}, at the same time, {third_event_subject} {third_event_predicate} {third_event_object}?"
                ],
            },
            "relation_duration": {
                "duration": [
                    "What is the duration of {first_event_subject} {first_event_predicate} {first_event_object} jointly when {second_event_subject} {second_event_predicate} {second_event_object} and {third_event_subject} {third_event_predicate} {third_event_object}?"
                ],
                "duration_compare": [
                    "Which one is {temporal_duration_rank} longest among {first_event_subject} {first_event_predicate} {first_event_object}, {second_event_subject} {second_event_predicate} {second_event_object}, {third_event_subject} {third_event_predicate} {third_event_object}?",
                ],
                "sum": [
                    "How long is the total duration of {first_event_subject} {first_event_predicate} {first_event_object}, {second_event_subject} {second_event_predicate} {second_event_object} and {third_event_subject} {third_event_predicate} {third_event_object}?"
                ],
                "average": [
                    "What is the average duration of {first_event_subject} {first_event_predicate} {first_event_object}, {second_event_subject} {second_event_predicate} {second_event_object} and {third_event_subject} {third_event_predicate} {third_event_object}?"
                ],
            },
            "relation_ranking": {
                "rank_start_time": [
                    "What is the rank of the event concerning {first_event_subject} based on start time among: {first_event_subject} {first_event_predicate} {first_event_object}, {second_event_subject} {second_event_predicate} {second_event_object} and {third_event_subject} {third_event_predicate} {third_event_object}?"
                ],
                "rank_end_time": [
                    "What is the rank of the event concerning {first_event_subject} based on end time among: {first_event_subject} {first_event_predicate} {first_event_object}, {second_event_subject} {second_event_predicate} {second_event_object} and {third_event_subject} {third_event_predicate} {third_event_object}?"
                ],
            },
        },
    },
}

QUESTION_TEMPLATES_PARAPHRASE_EXAMPLES = {
    "simple": {
        "temporal_constrained_retrieval": {
            "subject": (
                "Who member of sports team Vicenza Calcio from 1999-01-01 to 2000-01-01?",
                "Which individual was a member of Vicenza Calcio sports team from January, 1st 1999 to January, 1st 2000?",
            ),
            "object": (
                "Oscar Ahumada member of sports team which organisation from 2005-01-01 to 2009-01-01?",
                "Which sports team did Oscar Ahumada belong to between January 1st, 2005, and January 1st, 2009?",
            ),
        },
        "timeline_position_retrieval": {
            "timestamp_start": (
                "When did Giuseppe Cardone member of sports team Vicenza Calcio start?",
                "At what point did Giuseppe Cardone start his membership of Vicenza Calcio?",
            ),
            "timestamp_end": (
                "When did Giuseppe Cardone member of sports team Vicenza Calcio end?",
                "At what point did Giuseppe Cardone end his membership of Vicenza Calcio?",
            ),
            "timestamp_range": (
                "From when to when did Giuseppe Cardone member of sports team Vicenza Calcio?",
                "From when to when was Giuseppe Cardone a member of the Vicenza Calcio team?",
            ),
            "duration": (
                "How long did Hanna Walz position held member of the European Parliament?",
                "For what duration did Hanna Walz serve as a member of the European Parliament?",
            ),
        },
    },
    "medium": {
        "timeline_position_retrieval_temporal_constrained_retrieval": {
            "subject": {
                "before": (
                    "Prior to Friesland head of government Karin Evers-Meyer, Who/Which Organisation member of sports team England national under-21 football team?",
                    "Before Karin Evers-Meyer became the head of government in Friesland, who was a member of the England national under-21 football team?",
                ),
                "after": (
                    "After Gianluca Lamacchi member of sports team Genoa Cricket and Football Club, who/which organisation member of sports team Como 1907?",
                    "After Gianluca Lamacchi was a member of the Genoa Cricket and Football Club team, who was a member of the Como 1907 team?",
                ),
                "during": (
                    "Who/Which organisation member of sports team Unione Sportiva Città di Palermo while Deborah Kaplan spouse Breckin Meyer?",
                    "Who was a member of the Unione Sportiva Città di Palermo team while Deborah Kaplan was married to Breckin Meyer?",
                ),
                "start=start": (
                    "At the same time Charles Williams start position held Member of the 37th Parliament of the United Kingdom, who/which organisation starts member of sports team Italy national football team?",
                    "When Charles Williams began his term as a Member of the 37th Parliament of the United Kingdom, who became a member of the Italy national football team?",
                ),
                "end=end": (
                    "Who/which organisation finishes member of sports team Oldham Athletic A.F.C., at the same time Nadine Müller finish country of citizenship German Democratic Republic?",
                    "Who concluded their membership with the sports team Oldham Athletic A.F.C. at the time when Nadine Müller ceased to be a citizen of the German Democratic Republic?",
                ),
                "start=end": (
                    "When Elizabeth Amann ends employer Columbia University, who/which organisation starts member of sports team Brighton & Hove Albion F.C.?",
                    "When Elizabeth Amann ended her employment at Columbia University, who became a member of Brighton & Hove Albion F.C.?",
                ),
                "end=start": (
                    "When Rob Andrews starts position held United States representative, who/which organisation ends member of sports team Como 1907?",
                    "When Rob Andrews began his role as a United States representative, who left the sports team Como 1907?",
                ),
                "start<start": (
                    "Who/which organisation starts member of sports team Oldham Athletic A.F.C., before Nadine Müller starts country of citizenship German Democratic Republic?",
                    "Who started as a member of team Oldham Athletic A.F.C. before Nadine Müller obtained her citizenship of the German Democratic Republic?",
                ),
                "start>start": (
                    "Who/which organisation starts member of sports team Oldham Athletic A.F.C., after Nadine Müller starts country of citizenship German Democratic Republic?",
                    "Who started as a member of team Oldham Athletic A.F.C. after Nadine Müller obtained her citizenship of the German Democratic Republic?",
                ),
                "end<end": (
                    "Before Elizabeth Amann ends employer Columbia University, who/which organisation ends member of sports team Brighton & Hove Albion F.C.?",
                    "Before Elizabeth Amann ended her employment at Columbia University, who stopped being a member of Brighton & Hove Albion F.C.?",
                ),
                "end>end": (
                    "After Elizabeth Amann ends employer Columbia University, who/which organisation ends member of sports team Brighton & Hove Albion F.C.?",
                    "After Elizabeth Amann ended her employment at Columbia University, who stopped being a member of Brighton & Hove Albion F.C.?",
                ),
                "start<end": (
                    "Before Elizabeth Amann ends employer Columbia University, who/which organisation starts member of sports team Brighton & Hove Albion F.C.?",
                    "Before Elizabeth Amann ended her employment at Columbia University, who became a member of Brighton & Hove Albion F.C.?",
                ),
                "start>end": (
                    "After Elizabeth Amann ends employer Columbia University, who/which organisation starts member of sports team Brighton & Hove Albion F.C.?",
                    "After Elizabeth Amann ended her employment at Columbia University, who became a member of Brighton & Hove Albion F.C.?",
                ),
                "end<start": (
                    "Before Elizabeth Amann starts employer Columbia University, who/which organisation ends member of sports team Brighton & Hove Albion F.C.?",
                    "Before Elizabeth Amann started her employment at Columbia University, who stopped being a member of Brighton & Hove Albion F.C.?",
                ),
                "end>start": (
                    "After Elizabeth Amann starts employer Columbia University, who/which organisation ends member of sports team Brighton & Hove Albion F.C.?",
                    "After Elizabeth Amann started her employment at Columbia University, who stopped being a member of Brighton & Hove Albion F.C.?",
                ),
                "duration_before": (
                    "Who position held Prime Minister of Greece 10957 days before Aleksey Prokhorov award received Order of the Red Star?",
                    "Who was the Prime Minister of Greece 10957 before Aleksey Prokhorov received the Order of the Red Star?",
                ),
                "duration_after": (
                    "Who member of sports team Millwall F.C. 25202 days after Mario Varglien member of sports team Italy national football team?",
                    "Who was a member of Millwall F.C. 25202 days after Mario Varglien was a member of the Italy national football team?",
                ),
            },
            "object": {
                "before": (
                    "Who/What/Which organisation is member of sports teamed by Hal Robson-Kanu before Mike Thompson position held United States representative?",
                    "Who is a member of a sports team that included Hal Robson-Kanu before Mike Thompson held the position of United States representative?",
                ),
                "after": (
                    "Who/What/Which organisation is award receiveded by Harry Bolton Seed after Nikolay Rukavishnikov award received Order of Sukhbaatar?",
                    "What award was awarded to Harry Bolton Seed after Nikolay Rukavishnikov received the Order of Sukhbaatar?",
                ),
                "during": (
                    "Which organisation is significant evented Hurricane Darby while Tung Chan position held councillor?",
                    "Which organization was affected by the significant event of Hurricane Darby during the tenure of Tung Chan as a councillor?",
                ),
                "start=start": (
                    "At the same time Bärbel Höhn start position held member of the German Bundestag, in which organisation/what/who Gianvito Plasmati starts member of sports team?",
                    "When Bärbel Höhn began her role as a member of the German Bundestag, which sports team did Gianvito Plasmati join?",
                ),
                "end=end": (
                    "At the same time Noël Mamère finish position held member of the French National Assembly, in which organisation/who/what John Katko finishes position held?",
                    "When Noël Mamère ended his term as a member of the French National Assembly, which organization did John Katko leave?",
                ),
                "start=end": (
                    "At the same time Noël Mamère finish position held member of the French National Assembly, in which organisation/who/what John Katko starts position held?",
                    "When Noël Mamère ended his term as a member of the French National Assembly, which organization did John Katko join?",
                ),
                "end=start": (
                    "At the same time Noël Mamère starts position held member of the French National Assembly, in which organisation/who/what John Katko ends position held?",
                    "When Noël Mamère started his term as a member of the French National Assembly, which organization did John Katko leave?",
                ),
                "start<start": (
                    "Before Noël Mamère starts position held member of the French National Assembly, John Katko starts position held with which organisation/who/what?",
                    "Before Noël Mamère started his term as a member of the French National Assembly, which organization did John Katko join?",
                ),
                "start>start": (
                    "After Noël Mamère starts position held member of the French National Assembly, in which organisation/who/what John Katko starts position held?",
                    "After Noël Mamère started his term as a member of the French National Assembly, which organization did John Katko join?",
                ),
                "end<end": (
                    "Before Noël Mamère ends position held member of the French National Assembly, John Katko ends position held with which organisation/who/what?",
                    "Before Noël Mamère ended his term as a member of the French National Assembly, which organization did John Katko leave?",
                ),
                "end>end": (
                    "After Noël Mamère ends position held member of the French National Assembly, in which organisation/who/what John Katko ends position held?",
                    "After Noël Mamère ended his term as a member of the French National Assembly, which organization did John Katko leave?",
                ),
                "start<end": (
                    "Before Noël Mamère ends position held member of the French National Assembly, John Katko starts position held with which organisation/who/what?",
                    "Before Noël Mamère ended his term as a member of the French National Assembly, which organization did John Katko join?",
                ),
                "start>end": (
                    "After Noël Mamère ends position held member of the French National Assembly, in which organisation/who/what John Katko starts position held?",
                    "After Noël Mamère ended his term as a member of the French National Assembly, which organization did John Katko join?",
                ),
                "end<start": (
                    "Before Noël Mamère starts position held member of the French National Assembly, John Katko ends position held with which organisation/who/what?",
                    "Before Noël Mamère started his term as a member of the French National Assembly, which organization did John Katko leave?",
                ),
                "end>start": (
                    "After Noël Mamère starts position held member of the French National Assembly, in which organisation/who/what John Katko ends position held?",
                    "After Noël Mamère started his term as a member of the French National Assembly, which organization did John Katko leave?",
                ),
                "duration_before": (
                    "39082 days before Ana Miranda award received Ordem do Mérito Cultural, in which organisation/who/what Philip Stanhope, 1st Baron Weardale nominated for?",
                    "39082 Before Ana Miranda received the Ordem do Mérito Cultural award, what was Philip Stanhope nominated for?",
                ),
                "duration_after": (
                    "36159 days after Geoffrey Finsberg position held Member of the 48th Parliament of the United Kingdom, in which organisation/who/what Geoffrey Finsberg position held?",
                    "36159 days after Geoffrey Finsberg held the position of Member of the 48th Parliament of the United Kingdom, in which organisation did Geoffrey Finsberg hold a position?",
                ),
            },
        },
        "timeline_position_retrieval_timeline_position_retrieval": {
            "timestamp_range": {
                "intersection": (
                    "From when to when, Tom Hutchinson member of sports team Darlington F.C., at the same time, Giuseppe Iachini member of sports team Como 1907?",
                    "During which period was Tom Hutchinson a member of Darlington F.C. while Giuseppe Iachini was a member of Como 1907?",
                ),
            },
            "relation_allen": {
                "relation_allen": (
                    "What's the Allen temporal relation between Tom Hutchinson member of sports team Darlington F.C. and Giuseppe Iachini member of sports team Como 1907?",
                    "What's the Allen temporal relation between the time periods where Tom Hutchinson was a member of Darlington F.C. and Giuseppe Iachini was a member of Como 1907?",
                ),
            },
            "relation_duration": {
                # duration for the intersection of the two events
                "duration": (
                    "What is the duration of Tim Bishop position held United States representative jointly when Gianluca Zanetti member of sports team A.C. Cesena?",
                    "How long did Tim Bishop serve as a United States representative while Gianluca Zanetti's was a member of A.C. Cesena?",
                ),
                "duration_compare": (
                    "Is the duration of United States Seventh Fleet director/manager Robert F. Willard shorter the duration of Katrín Jakobsdóttir position held Member of the 2013-2016 Parliament of Iceland?",
                    "Was Robert F. Willard's tenure as director/manager of the United States Seventh Fleet shorter or longer than Katrín Jakobsdóttir's time serving as a Member of the 2013-2016 Parliament of Iceland?",
                ),
                "sum": (
                    "How long is the total duration of Association of Christian Democratic Students chairperson Jürgen Hardt and Giovanni Messe military rank lieutenant?",
                    "How long is the total duration of Jürgen Hardt mandate as a chairperson of the Association of Christian Democratic Students and Giovanni Messe time as a lieutenant?",
                ),
                "average": (
                    "What is the average duration of Christopher Price position held Member of the 44th Parliament of the United Kingdom and Colin Lee member of sports team Bristol City F.C.?",
                    "What is the average duration of Christopher Price's membership of the 44th Parliament of the United Kingdom and Colin Lee membership of Bristol City F.C.?",
                ),
            },
        },
    },
    "complex": {
        "timeline_position_retrieval*2+temporal_constrained_retrieval": {
            "subject": {
                "during&during": (
                    "Who/which organisation member of sports team Luton Town F.C., during Vladimír Mlynář position held editor-in-chief, during Sofie Ribbing work location The Hague?",
                    "Who was a member of Luton Town F.C., while Vladimír Mlynář held the position of editor-in-chief, and Sofie Ribbing worked in The Hague?",
                ),
                "before&after": (
                    "Who/which organisation member of sports team Luton Town F.C., before Vladimír Mlynář position held editor-in-chief, after Sofie Ribbing work location The Hague?",
                    "Who was a member of Luton Town F.C., before Vladimír Mlynář held the position of editor-in-chief, and after Sofie Ribbing worked in The Hague?",
                ),
                "start=start&start=end": (
                    "Who/which organisation starts member of sports team Luton Town F.C., at the same time as Vladimír Mlynář starts position held editor-in-chief, at the same time as Sofie Ribbing ends work location The Hague?",
                    "Who started being a member of Luton Town F.C. when Vladimír Mlynář started holding the position of editor-in-chief and Sofie Ribbing stopped working in The Hague?",
                ),
                "start<start&start>start": (
                    "Who/which organisation starts member of sports team Luton Town F.C., before Vladimír Mlynář starts position held editor-in-chief, after Sofie Ribbing starts work location The Hague?",
                    "Who started being a member of Luton Town F.C. before Vladimír Mlynář started holding the position of editor-in-chief and after Sofie Ribbing started working in The Hague?",
                ),
                "start<end&start>end": (
                    "Who/which organisation starts member of sports team Luton Town F.C., before Vladimír Mlynář ends position held editor-in-chief, after Sofie Ribbing ends work location The Hague?",
                    "Who started being a member of Luton Town F.C. before Vladimír Mlynář stopped holding the position of editor-in-chief and after Sofie Ribbing stopped working in The Hague?",
                ),
                "end=end&end=start": (
                    "Who/which organisation ends member of sports team Luton Town F.C., at the same time as Vladimír Mlynář ends position held editor-in-chief, at the same time as Sofie Ribbing starts work location The Hague?",
                    "Who stopped being a member of Luton Town F.C. when Vladimír Mlynář stopped holding the position of editor-in-chief and Sofie Ribbing started working in The Hague?",
                ),
                "end<end&end>end": (
                    "Who/which organisation ends member of sports team Luton Town F.C., before Vladimír Mlynář ends position held editor-in-chief, after Sofie Ribbing ends work location The Hague?",
                    "Who stopped being a member of Luton Town F.C. before Vladimír Mlynář stopped holding the position of editor-in-chief and after Sofie Ribbing stopped working in The Hague?",
                ),
                "end<start&end>start": (
                    "Who/which organisation ends member of sports team Luton Town F.C., before Vladimír Mlynář starts position held editor-in-chief, after Sofie Ribbing starts work location The Hague?",
                    "Who stopped being a member of Luton Town F.C. before Vladimír Mlynář started holding the position of editor-in-chief and after Sofie Ribbing started working in The Hague?",
                ),
                "duration_N(after|before)&duration_N(after|before)": (
                    "Who Affiliation To Finance / Economy / Commerce / Trade Ministry (Laos), 2302 days after Lawrence Gonzi Affiliation To Commonwealth of Nations, 1356 days after Algirdas Mykolas Brazauskas Affiliation To Social Democratic Party of Lithuania?",
                    "Who was affiliated to the Finance / Economy / Commerce / Trade Ministry (Laos), 2302 days after Lawrence Gonzi was affiliated to the Commonwealth of Nations, and 1356 days before Algirdas Mykolas Brazauskas was affiliated to the Social Democratic Party of Lithuania?",
                ),
            },
            "object": {
                "during&during": (
                    "Adalbert Schnee military rank who/what/which organisation, during Gerhard Hager position held member of the European Parliament, during Sofie Ribbing work location The Hague?",
                    "In which organisation did Adalbert Schnee held a military rank, while Gerhard Hager was a member of the European Parliament and Sofie Ribbing was working in The Hague?",
                ),
                "before&after": (
                    "Adalbert Schnee military rank who/what/which organisation, before Gerhard Hager position held member of the European Parliament, after Sofie Ribbing work location The Hague?",
                    "In which organisation did Adalbert Schnee held a military rank, before Gerhard Hager was a member of the European Parliament and after Sofie Ribbing was working in The Hague?",
                ),
                "start=start&start=end": (
                    "Adalbert Schnee starts military rank who/what/which organisation, at the time Gerhard Hager starts position held member of the European Parliament, at the time Sofie Ribbing ends work location The Hague?",
                    "In which organisation did Adalbert Schnee start to hold a military rank, at the same time as Gerhard Hager started being a member of the European Parliament and Sofie Ribbing stopped working in The Hague?",
                ),
                "start<start&start>start": (
                    "Adalbert Schnee starts military rank who/what/which organisation, before Gerhard Hager starts position held member of the European Parliament, after Sofie Ribbing starts work location The Hague?",
                    "In which organisation did Adalbert Schnee start to hold a military rank, before Gerhard Hager started being a member of the European Parliament and after Sofie Ribbing started working in The Hague?",
                ),
                "start<end&start>end": (
                    "Adalbert Schnee starts military rank who/what/which organisation, before Gerhard Hager ends position held member of the European Parliament, after Sofie Ribbing ends work location The Hague?",
                    "In which organisation did Adalbert Schnee start to hold a military rank, before Gerhard Hager stopped being a member of the European Parliament and after Sofie Ribbing stopped working in The Hague?",
                ),
                "end=end&end=start": (
                    "Adalbert Schnee ends military rank who/what/which organisation, at the time Gerhard Hager ends position held member of the European Parliament, at the time Sofie Ribbing starts work location The Hague?",
                    "In which organisation did Adalbert Schnee stop holding a military rank at the same time as Gerhard Hager stopped being a member of the European Parliament and Sofie Ribbing started working in The Hague?",
                ),
                "end<end&end>end": (
                    "Adalbert Schnee ends military rank who/what/which organisation, before Gerhard Hager ends position held member of the European Parliament, after Sofie Ribbing ends work location The Hague?",
                    "In which organisation did Adalbert Schnee stop holding a military rank before Gerhard Hager stopped being a member of the European Parliament and after Sofie Ribbing stopped working in The Hague?",
                ),
                "end<start&end>start": (
                    "Adalbert Schnee ends military rank who/what/which organisation, before Gerhard Hager starts position held member of the European Parliament, after Sofie Ribbing starts work location The Hague?",
                    "In which organisation did Adalbert Schnee stop holding a military rank before Gerhard Hager started being a member of the European Parliament and after Sofie Ribbing started working in The Hague?",
                ),
                "duration_N(after|before)&duration_N(after|before)": (
                    "Lien Thikeo Affiliation To which organisation/what/who, 2302 days after Lawrence Gonzi Affiliation To Commonwealth of Nations, 1356 days after Algirdas Mykolas Brazauskas Affiliation To Social Democratic Party of Lithuania?",
                    "To which organization was Lien Thikeo affiliated, 2302 days after Lawrence Gonzi was affiliated to the Commonwealth of Nations, and 1356 days before Algirdas Mykolas Brazauskas was affiliated to the Social Democratic Party of Lithuania?",
                ),
            },
        },
        "timeline_position_retrieval*3": {
            "timestamp_range": {
                "intersection": (
                    "From when to when, Clarence Godber Burton position held councillor, at the same time, Cyril Svoboda position held Member of the Chamber of Deputies of the Parliament of the Czech Republic, at the same time, 1978 Colgate International significant event occurrence?",
                    "From when to when did Clarence Godber Burton held the position of councillor while Cyril Svoboda was a member of the Chamber of Deputies of the Parliament of the Czech Republic and the 1978 Colgate International event occured?",
                ),
            },
            "relation_duration": {
                "duration": (
                    "What is the duration of George Nicoll Barnes position held Member of the 29th Parliament of the United Kingdom jointly when Walther Hermann Nernst nominated for Nobel Prize in Chemistry and Paul Karrer nominated for Nobel Prize in Chemistry?",
                    "What is the duration of George Nicoll Barnes' membership of the 29th Parliament of the United Kingdom while Walther Hermann Nernst was nominated for the Nobel Prize in Chemistry and Paul Karrer was nominated for the Nobel Prize in Chemistry?",
                ),
                "duration_compare": (
                    "Which one is 2nd longest among Paddy McGuire member of sports team Manchester City F.C., Llibert Cuatrecasas i Membrado position held Member of the Congress of Deputies of Spain, George Nicoll Barnes position held Member of the 29th Parliament of the United Kingdom?",
                    "Which one is the second longest among Paddy McGuire's membership in Manchester City F.C., Llibert Cuatrecasas i Membrado membership of the Congress of Deputies of Spain and George Nicoll Barnes' membership of the 29th Parliament of the United Kingdoms?",
                ),
                "sum": (
                    "How long is the total duration of Young Union chairperson Jürgen Echternach, Camille Mortenol military branch French Navy and Clarence Godber Burton position held councillor?",
                    "How long is the total duration of Jürgen Echternach time as the chairperson of Young Union, Camille Mortenol time in the French Navy and Clarence Godber Burton time as a councillor?",
                ),
                "average": (
                    "What is the average duration of Jacob van Zuylen van Nijevelt position held Prime Minister of the Netherlands, 1920 Summer Olympics significant event occurrence and Colin Lee member of sports team Bristol City F.C.?",
                    "What is the average duration of the time of Jacob van Zuylen van Nijevelt as the Prime Minister of the Netherlands, the 1920 Summer Olympics and Colin Lee time in Bristol City F.C.?",
                ),
            },
            "relation_ranking": {
                "rank_start_time": (
                    "What is the rank of the event concerning Marie Sara based on start time among: Marie Sara spouse Henri Leconte, John Landy award received Companion of the Order of Australia and Nikolay Rukavishnikov award received Order of Sukhbaatar?",
                    "What is the rank of the event concerning Marie Sara based on start time among Marie Sara being the spouse of Henri Leconte, John Landy reception of Companion of the Order of Australia award and Nikolay Rukavishnikov reception of the Order of Sukhbaatar award?",
                ),
                "rank_end_time": (
                    "What is the rank of the event concerning Marie Sara based on start time among Marie Sara spouse Henri Leconte, John Landy award received Companion of the Order of Australia and Nikolay Rukavishnikov award received Order of Sukhbaatar?",
                    "What is the rank of the event concerning Marie Sara based on end time among Marie Sara being the spouse of Henri Leconte, John Landy reception of Companion of the Order of Australia award and Nikolay Rukavishnikov reception of the Order of Sukhbaatar award?",
                ),
            },
        },
    },
}


def get_paraphrase_examples(question: Mapping) -> list[tuple[str, str]]:
    example = QUESTION_TEMPLATES_PARAPHRASE_EXAMPLES[question["question_level"]][
        question["question_type"]
    ][question["answer_type"]]

    if not isinstance(example, dict):
        return [example]

    timerange_relation_properties = (
        "(before"
        "|after"
        "|during"
        "|start=start"
        "|end=end"
        "|start=end"
        "|end=start"
        "|start<start"
        "|start>start"
        "|end<end"
        "|end>end"
        "|start<end"
        "|start>end"
        "|end<start"
        "|end>start)"
    )
    if re.match(
        r"{}&{}".format(timerange_relation_properties, timerange_relation_properties),
        question["temporal_relation"],
    ):
        tpr1, tpr2 = question["temporal_relation"].split("&")
        relevant_keys = [k for k in example.keys() if not k.startswith("duration_N")]
        relevant_keys = [k for k in relevant_keys if tpr1 in k or tpr2 in k]
        assert len(relevant_keys) <= 2
        return [example[k] for k in relevant_keys]
    # special handling for complex duration question
    # (temporal relation example: 'duration_234 days after&duration_during')
    elif re.match(r"duration_[^&]*&duration_[^&]*", question["temporal_relation"]):
        d1, d2 = question["temporal_relation"].split("&")
        relevant_keys = {"duration_N(after|before)&duration_N(after|before)"}
        d1_maybe_tpr = d1.replace("duration_", "")
        d2_maybe_tpr = d2.replace("duration_", "")
        relevant_keys |= {
            k for k in example.keys() if d1_maybe_tpr in k or d2_maybe_tpr in k
        }
        return [example[k] for k in relevant_keys]
    # general case: simply retrieve the example meant for
    # question["temporal_relation"]
    else:
        return [example[question["temporal_relation"]]]
