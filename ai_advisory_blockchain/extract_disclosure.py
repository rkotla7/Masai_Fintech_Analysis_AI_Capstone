"""
Part 3B -- Structured disclosure extraction.

extract_signals(snippet) -> {"risk_flags": [...], "hedging_detected": bool,
                              "sentiment": "confident"|"cautious"|"neutral"}

Mock mode (MOCK_LLM unset or "1", graded baseline): keyword/regex rules,
no network call. 
"""
import os
import re
from disclosure_snippets import DISCLOSURE_SNIPPETS

MOCK_LLM = os.environ.get("MOCK_LLM", "1") == "1"

RISK_KEYWORDS = {
    "litigation": "litigation risk",
    "regulatory": "regulatory risk",
    "notice": "regulatory risk",
    "customer": "customer concentration risk",  # combined with % check below
}
HEDGING_PHRASES = ["assuming", "cautiously", "visibility"]
CONFIDENT_WORDS = ["confident", "approved"]


def extract_signals(snippet: str) -> dict:
    text = snippet.lower()

    risk_flags = []
    if "litigation" in text:
        risk_flags.append("litigation risk")
    if "regulatory" in text or "notice" in text:
        risk_flags.append("regulatory risk")
    if "customer" in text and ("percent" in text or "%" in text):
        risk_flags.append("customer concentration risk")

    hedging_detected = any(phrase in text for phrase in HEDGING_PHRASES)

    if any(word in text for word in CONFIDENT_WORDS):
        sentiment = "confident"
    elif hedging_detected:
        sentiment = "cautious"
    else:
        sentiment = "neutral"

    return {
        "risk_flags": risk_flags,
        "hedging_detected": hedging_detected,
        "sentiment": sentiment,
    }


if __name__ == "__main__":
    print(f"MOCK_LLM = {MOCK_LLM}\n")
    lines = [f"# Part 3B - Disclosure Extraction Output (MOCK_LLM={MOCK_LLM})\n"]
    for snippet in DISCLOSURE_SNIPPETS:
        result = extract_signals(snippet)
        doc_id = snippet.split(":")[0]
        print(f"{doc_id}: {result}")
        lines.append(f"## {doc_id}\n")
        lines.append(f"> {snippet}\n")
        lines.append(f"- risk_flags: {result['risk_flags']}")
        lines.append(f"- hedging_detected: {result['hedging_detected']}")
        lines.append(f"- sentiment: {result['sentiment']}\n")
    log_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "extract_disclosure_output.md")

    with open(log_path, "w") as f:
        f.write("\n".join(lines))
    print(f"Saved {log_path}")
