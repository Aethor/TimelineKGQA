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
                    "Early than {second_event_subject} {second_event_predicate} {second_event_object}, Who/Which organisation {first_event_predicate} {first_event_object}?",
                    "Prior to {second_event_subject} {second_event_predicate} {second_event_object}, Who/Which organisation {first_event_predicate} {first_event_object}?",
                    "Who/Which Organisation {first_event_predicate} {first_event_object} ahead of {second_event_subject} {second_event_predicate} {second_event_object}?",
                    "Who/Which organisation {first_event_predicate} {first_event_object} preceding {second_event_subject} {second_event_predicate} {second_event_object}?",
                    "Who/Which organisation {first_event_predicate} {first_event_object} earlier than {second_event_subject} {second_event_predicate} {second_event_object}?",
                    "Who/Which organisation {first_event_predicate} {first_event_object} in advance of {second_event_subject} {second_event_predicate} {second_event_object}?",
                ],
                "after": [
                    "Who {second_event_predicate} {second_event_object} {temporal_relation} {first_event_subject} {first_event_predicate} {first_event_object}?",
                    "{temporal_relation} {first_event_subject} {first_event_predicate} {first_event_object}, who {second_event_predicate} {second_event_object}?",
                ],
                "during": [
                    "Who {first_event_predicate} {first_event_object} during {second_event_subject} {second_event_predicate} {second_event_object}?",
                    "during {second_event_subject} {second_event_predicate} {second_event_object}, who {first_event_predicate} {first_event_object}?",
                    "Who {first_event_predicate} {first_event_object} while {second_event_subject} {second_event_predicate} {second_event_object}?",
                    "while {second_event_subject} {second_event_predicate} {second_event_object}, who {first_event_predicate} {first_event_object}?",
                    "Who {first_event_predicate} {first_event_object} in the course of {second_event_subject} {second_event_predicate} {second_event_object}?",
                    "In the midst of {second_event_subject} {second_event_predicate} {second_event_object}, who {first_event_predicate} {first_event_object}?",
                    "Who {first_event_predicate} {first_event_object} at the same time {second_event_subject} {second_event_predicate} {second_event_object}?",
                ],
                "meets": [
                    # This means first end time = second start time
                    "When {second_event_subject} starts {second_event_predicate} {second_event_object}, who ends {first_event_predicate} {first_event_object}?",
                    "Who ends {first_event_predicate} {first_event_object} when {second_event_subject} starts {second_event_predicate} {second_event_object}?",
                ],
                "metby": [
                    # This means first start time = second end time
                    "When {second_event_subject} ends {second_event_predicate} {second_event_object}, who starts {first_event_predicate} {first_event_object}?",
                    "Who starts {first_event_predicate} {first_event_object} when {second_event_subject} ends {second_event_predicate} {second_event_object}?",
                ],
                "starts": [
                    # This means first and second start at the same time, however, the end time of the first event is before the end time of the second event
                    "Who starts {first_event_predicate} {first_event_object}, at the same time {second_event_subject} start {second_event_predicate} {second_event_object}?",
                    "At the same time {second_event_subject} start {second_event_predicate} {second_event_object}, who starts {first_event_predicate} {first_event_object}?",
                ],
                "startedby": [
                    # This means first and second start at the same time, however, the end time of the first event is after the end time of the second event
                    "Who starts {first_event_predicate} {first_event_object}, at the same time {second_event_subject} start {second_event_predicate} {second_event_object}?",
                    "At the same time {second_event_subject} start {second_event_predicate} {second_event_object}, who starts {first_event_predicate} {first_event_object}?",
                ],
                "finishes": [
                    # This means first and second finish at the same time, however, the start time of the first event is after the start time of the second event
                    "Who finishes {first_event_predicate} {first_event_object}, at the same time {second_event_subject} finish {second_event_predicate} {second_event_object}?",
                    "At the same time {second_event_subject} finish {second_event_predicate} {second_event_object}, who finishes {first_event_predicate} {first_event_object}?",
                ],
                "finishedby": [
                    # This means first and second finish at the same time, however, the start time of the first event is before the start time of the second event
                    "Who finishes {first_event_predicate} {first_event_object}, at the same time {second_event_subject} finish {second_event_predicate} {second_event_object}?",
                    "At the same time {second_event_subject} finish {second_event_predicate} {second_event_object}, who finishes {first_event_predicate} {first_event_object}?",
                ],
                "equal": [
                    # This means first and second start and end at the same time
                    "Who {first_event_predicate} {first_event_object}, at the same time {second_event_subject} {second_event_predicate} {second_event_object}?",
                    "Who {first_event_predicate} {first_event_object} at the same start and end time {second_event_subject} start and end {second_event_predicate} {second_event_object}?",
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
                    "Who/What/Which organisation is {first_event_predicate}ed {first_event_subject} in the course of {second_event_subject} {second_event_predicate} {second_event_object}?",
                ],
                "meets": [
                    # This means first end time = second start time, this question is asking for the first object
                    "{second_event_subject} starts {second_event_predicate} {second_event_object} at the same time {first_event_subject} ends {first_event_predicate} with who/what/which organisation?",
                ],
                "metby": [
                    # This means first start time = second end time, this question is asking for the first object
                    "{second_event_subject} ends {second_event_predicate} {second_event_object} at the same time {first_event_subject} starts {first_event_predicate} with who/what/which organisation?",
                ],
                "starts": [
                    # This means first and second start at the same time, however, the end time of the first event is before the end time of the second event
                    "At the same time {second_event_subject} start {second_event_predicate} {second_event_object}, in which organisation/what/who {first_event_subject} starts {first_event_predicate}?",
                ],
                "startedby": [
                    # This means first and second start at the same time, however, the end time of the first event is after the end time of the second event
                    "At the same time {second_event_subject} start {second_event_predicate} {second_event_object}, in which organisation/what/who {first_event_subject} starts {first_event_predicate}?",
                ],
                "finishes": [
                    # This means first and second finish at the same time, however, the start time of the first event is after the start time of the second event
                    "At the same time {second_event_subject} finish {second_event_predicate} {second_event_object}, in which organisation/what/who {first_event_subject} finishes {first_event_predicate}?",
                ],
                "finishedby": [
                    # This means first and second finish at the same time, however, the start time of the first event is before the start time of the second event
                    "At the same time {second_event_subject} finish {second_event_predicate} {second_event_object}, in which organisation/what/who {first_event_subject} finishes {first_event_predicate}?",
                ],
                "equal": [
                    # This means first and second start and end at the same time
                    "At the same time {second_event_subject} {second_event_predicate} {second_event_object}, in which organisation/what/who {first_event_subject} {first_event_predicate}?",
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
            "relation_union_or_intersection": {
                "intersection": [
                    "From when to when, {first_event_subject} {first_event_predicate} {first_event_object}, at the same time, {second_event_subject} {second_event_predicate} {second_event_object}?"
                ],
            },
            # we are looking for the allen temporal relation between the two events, so the question normally is asked for relation directly, or true/false question.
            # However, it is still possible to have specific format for specific relationship question, even it is true/false question.
            # We will do choice and random for now, consider this later.
            "relation_allen": {
                # "X < Y": [],
                # "X m Y": [],
                # "X o Y": [],
                # "X fi Y": [],
                # "X di Y": [],
                # "X s Y": [],
                # "X = Y": [],
                # "X si Y": [],
                # "X d Y": [],
                # "X f Y": [],
                # "X oi Y": [],
                # "X mi Y": [],
                # "X > Y": [],
                "choice": [
                    "What's the Allen temporal relation between {first_event_subject} {first_event_predicate} {first_event_object} and {second_event_subject} {second_event_predicate} {second_event_object}?",
                ],
                "true_false": [
                    "Is '{temporal_relation}' the correct Allen temporal relation between {first_event_subject} {first_event_predicate} {first_event_object} and {second_event_subject} {second_event_predicate} {second_event_object}?",
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
            "subject": [
                "Who {first_event_predicate} {first_event_object}, {temporal_relation_12} {second_event_subject} {second_event_predicate} {second_event_object}, {temporal_relation_13} {third_event_subject} {third_event_predicate}, {third_event_object}?",
            ],
            "object": [
                "{first_event_subject} {first_event_predicate} which organisation/what/who, {temporal_relation_12} {second_event_subject} {second_event_predicate} {second_event_object}, {temporal_relation_13} {third_event_subject} {third_event_predicate} {third_event_object}?",
            ],
        },
        "timeline_position_retrieval*3": {
            "relation_union_or_intersection": {
                "intersection": [
                    "From when to when, {first_event_subject} {first_event_predicate} {first_event_object}, at the same time, {second_event_subject} {second_event_predicate} {second_event_object}, at the same time, {third_event_subject} {third_event_predicate} {third_event_object}?"
                ],
            },
            # TODO: this is not really make sense, so we ignore it here
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
                    "After Gianluca Lamacchi member of sports team Genoa Cricket and Football Club, who member of sports team Como 1907?",
                    "After Gianluca Lamacchi was a member of the Genoa Cricket and Football Club team, who was a member of the Como 1907 team?",
                ),
                "during": (
                    "Who member of sports team Unione Sportiva Città di Palermo in the course of Deborah Kaplan spouse Breckin Meyer?",
                    "Who was a member of the Unione Sportiva Città di Palermo team while Deborah Kaplan was married to Breckin Meyer?",
                ),
                "meets": (
                    # This means first end time = second start time
                    "When Rob Andrews starts position held United States representative, who ends member of sports team Como 1907?",
                    "When Rob Andrews began his role as a United States representative, who left the sports team Como 1907?",
                ),
                "metby": (
                    # This means first start time = second end time
                    "When Elizabeth Amann ends employer Columbia University, who starts member of sports team Brighton & Hove Albion F.C.?",
                    "When Elizabeth Amann ended her employment at Columbia University, who became a member of Brighton & Hove Albion F.C.?",
                ),
                "starts": (  # This means first and second start at the same time, however, the end time of the first event is before the end time of the second event
                    "At the same time Charles Williams start position held Member of the 37th Parliament of the United Kingdom, who starts member of sports team Italy national football team?",
                    "When Charles Williams began his term as a Member of the 37th Parliament of the United Kingdom, who became a member of the Italy national football team?",
                ),
                "startedby": (  # This means first and second start at the same time, however, the end time of the first event is after the end time of the second event
                    "At the same time Fran Walsh start award received Nebula Award for Best Script, who starts member of sports team Unione Calcio Sampdoria?",
                    "When Fran Walsh received the Nebula Award for Best Script, who became a member of the Unione Calcio Sampdoria sports team?",
                ),
                "finishes": (  # This means first and second finish at the same time, however, the start time of the first event is after the start time of the second event
                    "Who finishes member of sports team Oldham Athletic A.F.C., at the same time Nadine Müller finish country of citizenship German Democratic Republic?",
                    "Who concluded their membership with the sports team Oldham Athletic A.F.C. at the time when Nadine Müller ceased to be a citizen of the German Democratic Republic?",
                ),
                "finishedby": (
                    # This means first and second finish at the same time, however, the start time of the first event is before the start time of the second event
                    "Who finishes position held United States senator, at the same time Josh Rees finish member of sports team Brentford F.C.?",
                    "Who ended their tenure as a United States senator when Josh Rees ended his time as a member of Brentford F.C.?",
                ),
                "equal": (
                    # This means first and second start and end at the same time
                    "Who position held United States representative at the same start and end time Jeff Whitley start and end member of sports team Sunderland A.F.C.?",
                    "Who started and ended holding the position of United States representative at the same time as the arrival and departure of Jeff Whitley as a member of Sunderland A.F.C.?",
                ),
                "duration_before": (
                    "Who position held Prime Minister of Greece 10957 days before Aleksey Prokhorov award received Order of the Red Star?",
                    "Who was the Prime Minister of Greece 10957 before Aleksey Prokhorov received the Order of the Red Star?",
                ),
                "duration_after": (
                    "Who member of sports team Millwall F.C. 25202 days after Mario Varglien member of sports team Italy national football team?",
                    "25202 days after Mario Varglien was a member of the Italy national football team, who was a member of Millwall F.C.?",
                ),
            },
            "object": {
                "before": (
                    "Who/What/Which organisation is member of sports teamed by Hal Robson-Kanu before Mike Thompson position held United States representative?",
                    "Before Mike Thompson held the position of United States representative, who is a member of a sports team that included Hal Robson-Kanu as a member?",
                ),
                "after": (
                    "Who/What/Which organisation is award receiveded by Harry Bolton Seed after Nikolay Rukavishnikov award received Order of Sukhbaatar?",
                    "After Nikolay Rukavishnikov received the Order of Sukhbaatar, what award was awarded Harry Bolton Seed?",
                ),
                "during": (
                    "Which organisation is significant evented Hurricane Darby while Tung Chan position held councillor?",
                    "During the tenure of Tung Chan as a councillor, which organization was affected by the significant event of Hurricane Darby?",
                ),
                "meets": (
                    # This means first end time = second start time, this question is asking for the first object
                    "Rob Andrews starts position held United States representative at the same time Dan Twardzik ends member of sports team with who/what/which organisation?",
                    "When Rob Andrews begins his role as a United States representative, which sports team does Dan Twardzik leave?",
                ),
                "metby": (
                    # This means first start time = second end time, this question is asking for the first object
                    "Mike McIntyre ends position held United States representative at the same time Rob Andrews starts position held with who/what/which organisation?",
                    "As Mike McIntyre finishes his tenure as a United States representative, Which organization does Rob Andrews begin working for?",
                ),
                "starts": (
                    # This means first and second start at the same time, however, the end time of the first event is before the end time of the second event
                    "At the same time Bärbel Höhn start position held member of the German Bundestag, in which organisation/what/who Gianvito Plasmati starts member of sports team?",
                    "When Bärbel Höhn began her role as a member of the German Bundestag, which sports team did Gianvito Plasmati join?",
                ),
                "startedby": (
                    # This means first and second start at the same time, however, the end time of the first event is after the end time of the second event
                    "At the same time Micky Holmes start member of sports team Northampton Town F.C., in which organisation/who/what Olivier Dassault starts position held?",
                    "When Micky Holmes became a member of Northampton Town F.C., with which organization did Olivier Dassault begin his position?",
                ),
                "finishes": (
                    # This means first and second finish at the same time, however, the start time of the first event is after the start time of the second event
                    "At the same time Noël Mamère finish position held member of the French National Assembly, in which organisation/who/what John Katko finishes position held?",
                    "When Noël Mamère ended his term as a member of the French National Assembly, which organization did John Katko leave?",
                ),
                "finishedby": (
                    # This means first and second finish at the same time, however, the start time of the first event is before the start time of the second event
                    "At the same time Ruud Gullit finish member of sports team A.C. Milan, in which organisation Alberto Malusci finishes member of sports team",
                    "When Ruud Gullit ended his time with A.C. Milan, which sports team did Alberto Malusci leave?",
                ),
                "equal": (
                    # This means first and second start and end at the same time
                    "At the same time Peter Mandelson position held Secretary of State for Business, Energy and Industrial Strategy, in which organisation/who/what Robinho member of sports team?",
                    "At the same time as Mandelson was serving as the Secretary of State for Business, Energy and Industrial Strategy, which sports team was Robinho a member of?",
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
            # because it is the time range, then we should also ask about the duration
            "relation_union_or_intersection": {
                "intersection": (
                    "From when to when, Tom Hutchinson member of sports team Darlington F.C., at the same time, Giuseppe Iachini member of sports team Como 1907?",
                    "During which period was Tom Hutchinson a member of Darlington F.C. while Giuseppe Iachini was a member of Como 1907?",
                ),
            },
            # we are looking for the allen temporal relation between the two events, so the question normally is asked for relation directly, or true/false question.
            # However, it is still possible to have specific format for specific relationship question, even it is true/false question.
            # We will do choice and random for now, consider this later.
            "relation_allen": {
                # "X < Y": [],
                # "X m Y": [],
                # "X o Y": [],
                # "X fi Y": [],
                # "X di Y": [],
                # "X s Y": [],
                # "X = Y": [],
                # "X si Y": [],
                # "X d Y": [],
                # "X f Y": [],
                # "X oi Y": [],
                # "X mi Y": [],
                # "X > Y": [],
                "choice": (
                    "What's the Allen temporal relation between Tom Hutchinson member of sports team Darlington F.C. and Giuseppe Iachini member of sports team Como 1907?",
                    "What's the Allen temporal relation between the time intervals where Tom Hutchinson was a member of Darlington F.C. and Giuseppe Iachini was a member of Como 1907?",
                ),
                "true_false": (
                    "Is the Allen temporal relation between Tom Hutchinson member of sports team Darlington F.C. during Giuseppe Iachini member of sports team Como 1907?",
                    "Is 'during' the correct Allen temporal relation between the time intervals where Tom Hutchinson was a member of Darlington F.C. and Giuseppe Iachini was a member of Como 1907?",
                ),
            },
            "relation_duration": {
                # duration for the intersection of the two events
                "duration": (
                    "What is the duration of Tim Bishop position held United States representative jointly when Gianluca Zanetti member of sports team A.C. Cesena?",
                    "During Gianluca Zanetti's tenure as a member of A.C. Cesena, how long did Tim Bishop serve as a United States representative concurrently?",
                ),
                "duration_compare": (
                    "Is the duration of United States Seventh Fleet director/manager Robert F. Willard shorter the duration of Katrín Jakobsdóttir position held Member of the 2013-2016 Parliament of Iceland?",
                    "Was Robert F. Willard's tenure as director/manager of the United States Seventh Fleet shorter than Katrín Jakobsdóttir's time serving as a Member of the 2013-2016 Parliament of Iceland?",
                ),
                # This is actually for union
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
            "subject": (
                "Who member of sports team Luton Town F.C., after Vladimír Mlynář position held editor-in-chief, after Sofie Ribbing work location, The Hague?",
                "Who was a member of the sports team Luton Town F.C., after Vladimír Mlynář held the position of editor-in-chief and Sofie Ribbing worked in The Hague?",
            ),
            "object": (
                "Adalbert Schnee military rank who/what/which organisation, before Gerhard Hager position held member of the European Parliament, before k.d. lang nominated for Juno Award for Single of the Year?",
                "In which organization did Adalbert Schnee hold a military rank, before Gerhard Hager was a member of the European Parliament and before k.d. lang was nominated for the Juno Award for Single of the Year?",
            ),
        },
        "timeline_position_retrieval*3": {
            "relation_union_or_intersection": {
                "intersection": (
                    "From when to when, Clarence Godber Burton position held councillor, at the same time, Cyril Svoboda position held Member of the Chamber of Deputies of the Parliament of the Czech Republic, at the same time, 1978 Colgate International significant event occurrence?",
                    "From when to when did Clarence Godber Burton held the position of councillor while Cyril Svoboda was a member of the Chamber of Deputies of the Parliament of the Czech Republic and the 1978 Colgate International event occured?",
                ),
            },
            # TODO: this is not really make sense, so we ignore it here
            "relation_duration": {
                "duration": (
                    "What is the duration of George Nicoll Barnes position held Member of the 29th Parliament of the United Kingdom jointly when Walther Hermann Nernst nominated for Nobel Prize in Chemistry and Paul Karrer nominated for Nobel Prize in Chemistry?",
                    "What is the duration of George Nicoll Barnes' membership of the 29th Parliament of the United Kingdom while Walther Hermann Nernst was nominated for the Nobel Prize in Chemistry and Paul Karrer was nominated for the Nobel Prize in Chemistry?",
                ),
                "duration_compare": (
                    "Which one is 2 longest among Paddy McGuire member of sports team Manchester City F.C., Llibert Cuatrecasas i Membrado position held Member of the Congress of Deputies of Spain, George Nicoll Barnes position held Member of the 29th Parliament of the United Kingdom?",
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
