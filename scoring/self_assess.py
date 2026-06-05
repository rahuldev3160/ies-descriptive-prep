RUBRICS: dict[str, list[dict]] = {
    "essay": [
        {"id": "thesis",     "text": "Clear thesis statement in introduction",                            "weight": 2},
        {"id": "peel",       "text": "Body paragraphs use PEEL structure (Point → Evidence → Explain → Link)", "weight": 2},
        {"id": "evidence",   "text": "At least one specific example, data point, or policy reference",   "weight": 1},
        {"id": "policy",     "text": "Conclusion includes policy implication or 'Way Forward'",           "weight": 1},
        {"id": "no_new_arg", "text": "No new argument or evidence introduced in conclusion",              "weight": 1},
        {"id": "flow",       "text": "Logical flow between paragraphs (no abrupt topic jumps)",          "weight": 1},
    ],
    "précis": [
        {"id": "third_person", "text": "Written entirely in third person throughout",                     "weight": 2},
        {"id": "word_count",   "text": "Word count within ±10% of target",                               "weight": 2},
        {"id": "no_lifted",    "text": "No lifted phrases — own words used (except technical terms)",    "weight": 2},
        {"id": "title",        "text": "Title given in Introduction section (under 10 words)",            "weight": 1},
        {"id": "no_opinion",   "text": "No personal opinion or external knowledge added",                 "weight": 2},
        {"id": "sequence",     "text": "Original logical sequence of the passage maintained",            "weight": 1},
    ],
    "rc": [
        {"id": "direct_first",  "text": "Direct answer given in the first sentence",                     "weight": 2},
        {"id": "passage_only",  "text": "Answer based only on passage content (no external knowledge)",  "weight": 3},
        {"id": "no_copy",       "text": "Not copied verbatim from the passage (own words)",               "weight": 1},
    ],
    "letter": [
        {"id": "subject_line",  "text": "Subject line present (Sub: ...)",                               "weight": 2},
        {"id": "salutation",    "text": "Correct salutation for letter type (Sir/Madam vs Dear Mr./Ms.)", "weight": 1},
        {"id": "no_contraction","text": "No contractions used (I'm→I am, don't→do not)",                 "weight": 1},
        {"id": "designation",   "text": "Sender identified by designation, not personal name",           "weight": 1},
        {"id": "close_match",   "text": "Close matches salutation (Yours faithfully / Yours sincerely)", "weight": 1},
    ],
    "report": [
        {"id": "title_caps",    "text": "Title in full capitals",                                         "weight": 1},
        {"id": "metadata",      "text": "Metadata block complete (To / From / Date / Sub)",              "weight": 2},
        {"id": "findings_sep",  "text": "Findings and Recommendations in separate labelled sections",    "weight": 2},
        {"id": "impersonal",    "text": "Impersonal language throughout (no 'I think' / 'we believe')",  "weight": 2},
        {"id": "action_verbs",  "text": "Recommendations use action verbs (Install / Train / Allocate)", "weight": 1},
    ],
}


def compute_self_assess_score(type_id: str, checks: dict[str, bool]) -> float:
    criteria = RUBRICS.get(type_id.lower(), [])
    if not criteria:
        return 0.0
    total = sum(c["weight"] for c in criteria)
    earned = sum(c["weight"] for c in criteria if checks.get(c["id"], False))
    return earned / total if total > 0 else 0.0
