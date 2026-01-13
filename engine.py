import json
import re

def load_rules(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def keyword_to_regex(keyword: str) -> str:
    kw = re.escape(keyword)
    kw = kw.replace("\\ ", r"[\s\-_]?")

    if len(keyword.split()) == 1:
        kw = r"\b" + kw + r"\b"

    return kw

def build_regex_rulebase(raw_rules: dict):
    return {
        "required_keywords": raw_rules["required_keywords"],

        "forbidden_keywords": [
            keyword_to_regex(k) for k in raw_rules["forbidden_keywords"]
        ]
    }

def check_required(text: str, rulebase: dict):
    violations = []

    for req in rulebase["required_keywords"]:
        if req.lower() not in text.lower():
            violations.append({
                "type": "required_missing",
                "missing": req
            })

    return violations

def check_forbidden(text: str, rulebase: dict):
    violations = []
    highlights = []

    for patt in rulebase["forbidden_keywords"]:
        for m in re.finditer(patt, text):
            span = m.span()
            violations.append({
                "type": "forbidden_detected",
                "keyword": m.group(),
                "position": span
            })

            highlights.append({
                "matched": m.group(),
                "start": span[0],
                "end": span[1]
            })

    return violations, highlights

def run_qc(script: str, rulebase: dict):

    rulebase = build_regex_rulebase(rulebase)
    text = script.lower()

    required_violations = check_required(text, rulebase)
    forbidden_violations, highlights = check_forbidden(text, rulebase)

    # Pass/fail check
    is_passed = len(required_violations) == 0 and len(forbidden_violations) == 0

    return {
        "required_violations": required_violations,
        "forbidden_violations": forbidden_violations,
        "highlights": highlights,
        "is_passed": is_passed
    }