import re
from difflib import SequenceMatcher
from .normaliser import normalize

_MIN_WORDS = 8
_STUFFING_DENSITY = 0.5  # keyword hits per sentence threshold


def _fuzzy_match(needle: str, haystack: str, threshold: float) -> bool:
    needle_words = needle.split()
    haystack_words = haystack.split()
    n = len(needle_words)
    if n > len(haystack_words):
        return False
    for i in range(len(haystack_words) - n + 1):
        window = " ".join(haystack_words[i : i + n])
        if SequenceMatcher(None, needle, window).ratio() >= threshold:
            return True
    if n == 1:
        for hw in haystack_words:
            if SequenceMatcher(None, needle, hw).ratio() >= threshold:
                return True
    return False


def _match_keyword(kw: dict, norm_text: str) -> bool:
    threshold = kw.get("fuzzy_threshold", 0.82)
    for variant in kw.get("variants", [kw.get("canonical", "")]):
        nv = normalize(variant)
        if nv and nv in norm_text:
            return True
    for variant in kw.get("variants", [kw.get("canonical", "")]):
        nv = normalize(variant)
        if nv and _fuzzy_match(nv, norm_text, threshold):
            return True
    return False


def _detect_stuffing(norm_text: str, hit_count: int, word_count: int) -> bool:
    if word_count < 30:
        return hit_count >= 4
    sentences = [s.strip() for s in re.split(r"[.!?]+", norm_text) if len(s.strip().split()) > 3]
    if not sentences:
        return False
    return (hit_count / len(sentences)) > _STUFFING_DENSITY


def score_section(section_schema: dict, raw_text: str) -> dict:
    words = (raw_text or "").split()
    wc = len(words)

    if wc == 0:
        return {"score": 0.0, "req_hits": [], "req_misses": [], "bon_hits": [],
                "phr_hits": [], "neg_hits": [], "word_count": 0, "empty": True}
    if wc < _MIN_WORDS:
        return {"score": 0.0, "req_hits": [], "req_misses": [], "bon_hits": [],
                "phr_hits": [], "neg_hits": [], "word_count": wc, "too_short": True}

    norm = normalize(raw_text)

    required = section_schema.get("required", [])
    bonus    = section_schema.get("bonus", [])
    phrases  = section_schema.get("phrases", [])
    negatives = section_schema.get("negative", [])

    req_hits, req_misses = [], []
    total_req_w = sum(k["weight"] for k in required) if required else 1.0
    for kw in required:
        (req_hits if _match_keyword(kw, norm) else req_misses).append(kw["canonical"])
    req_score = (sum(k["weight"] for k in required if k["canonical"] in req_hits) / total_req_w
                 if total_req_w > 0 else 1.0)

    bon_hits = [kw["canonical"] for kw in bonus if _match_keyword(kw, norm)]
    total_bon_w = sum(k["weight"] for k in bonus) if bonus else 0.0
    bon_score = (sum(k["weight"] for k in bonus if k["canonical"] in bon_hits) / total_bon_w
                 if total_bon_w > 0 else 0.0)

    phr_hits = [p["phrase"] for p in phrases if normalize(p["phrase"]) in norm]
    total_phr_w = sum(p["weight"] for p in phrases) if phrases else 0.0
    phr_score = (sum(p["weight"] for p in phrases if p["phrase"] in phr_hits) / total_phr_w
                 if total_phr_w > 0 else 0.0)

    neg_hits, penalty = [], 0.0
    for neg in negatives:
        if _match_keyword(neg, norm):
            neg_hits.append(neg["canonical"])
            penalty += neg.get("penalty", 0.3)
    penalty = min(penalty, 0.4)

    raw = min((req_score * 0.85) + (bon_score * 0.15) + (phr_score * 0.10), 1.0)
    score = max(raw - penalty, 0.0)

    all_hits = len(req_hits) + len(bon_hits) + len(phr_hits)
    stuffing = _detect_stuffing(norm, all_hits, wc)
    if stuffing:
        score = min(score, 0.40)

    return {
        "score": round(score, 4),
        "req_hits": req_hits,
        "req_misses": req_misses,
        "bon_hits": bon_hits,
        "phr_hits": phr_hits,
        "neg_hits": neg_hits,
        "word_count": wc,
        "stuffing": stuffing,
    }


def score_answer(sections_schema: dict, section_weights: dict,
                 intro: str, body: str, conclusion: str) -> dict:
    results = {}
    for name, text in [("intro", intro), ("body", body), ("conclusion", conclusion)]:
        results[name] = score_section(sections_schema.get(name, {}), text)

    w_i = section_weights.get("intro", 0.15)
    w_b = section_weights.get("body", 0.70)
    w_c = section_weights.get("conclusion", 0.15)
    total_w = w_i + w_b + w_c or 1.0

    overall = (
        results["intro"]["score"]      * (w_i / total_w) +
        results["body"]["score"]       * (w_b / total_w) +
        results["conclusion"]["score"] * (w_c / total_w)
    )
    return {
        "overall_score": round(overall, 4),
        "overall_pct":   round(overall * 100, 1),
        "sections":      results,
        "weights":       {"intro": w_i / total_w, "body": w_b / total_w, "conclusion": w_c / total_w},
    }


def build_feedback(score_result: dict) -> dict:
    def _grade(s: float) -> str:
        if s >= 0.85: return "Excellent"
        if s >= 0.70: return "Good"
        if s >= 0.55: return "Satisfactory"
        if s >= 0.40: return "Needs Work"
        return "Insufficient"

    def _hint(sec: dict, name: str) -> str:
        if sec.get("empty"):      return "No text submitted for this section."
        if sec.get("too_short"):  return f"Too short ({sec['word_count']} words). Write at least {_MIN_WORDS} words."
        if sec.get("stuffing"):   return "Very short with many keywords — expand your reasoning."
        if sec["neg_hits"]:       return f"Possible misconception: '{sec['neg_hits'][0]}'. Review this concept."
        if sec["req_misses"]:
            n = len(sec["req_misses"])
            return f"Missing key concept{'s' if n>1 else ''}: '{sec['req_misses'][0]}'" + (f" (+{n-1} more)" if n > 1 else "")
        if sec["score"] >= 0.85:  return f"Strong {name}. All key concepts present."
        return "Cover the core mechanism more explicitly."

    fb = {
        "overall_pct": score_result["overall_pct"],
        "grade": _grade(score_result["overall_score"]),
        "nailed": [],
        "missing": [],
        "sections": {},
    }

    intro_hits = set(score_result["sections"]["intro"]["req_hits"])
    body_hits  = set(score_result["sections"]["body"]["req_hits"])

    for name in ("intro", "body", "conclusion"):
        sec = score_result["sections"][name]
        hint = _hint(sec, name)

        conc_misses = set(score_result["sections"]["conclusion"]["req_misses"])
        if name == "conclusion" and (conc_misses & intro_hits):
            displaced = list(conc_misses & intro_hits)[0]
            hint += f" ('{displaced}' was in your intro — move policy points to conclusion.)"

        fb["sections"][name] = {
            "score_pct":      round(sec["score"] * 100, 1),
            "keywords_hit":   sec["req_hits"] + sec["bon_hits"],
            "keywords_missed":sec["req_misses"],
            "misconceptions": sec["neg_hits"],
            "hint":           hint,
            "word_count":     sec["word_count"],
        }
        fb["nailed"].extend(sec["req_hits"][:2])
        fb["missing"].extend(sec["req_misses"])

    fb["nailed"]  = list(dict.fromkeys(fb["nailed"]))
    fb["missing"] = list(dict.fromkeys(fb["missing"]))
    return fb
