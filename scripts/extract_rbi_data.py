"""
Extract RBI-exam-relevant data from UPSC economy PDFs.
Outputs a compact fact sheet to data/rbi_current_data.txt.
"""
import re
import subprocess
import sys
from pathlib import Path

ECONOMY_DIR = Path.home() / "Desktop/UPSC/Prelims/Economy"

PDFS = {
    "eco_survey_2526": ECONOMY_DIR / "Economic Survey 2025-26.pdf",
    "budget_highlights": ECONOMY_DIR / "Budget_Highlights_2026.pdf",
    "budget_analysis":   ECONOMY_DIR / "Union_Budget_Analysis-2026-27.pdf",
    "budget_tax":        ECONOMY_DIR / "taxreform_Budget_2026.pdf",
    "pt365":             ECONOMY_DIR / "Economy_PT 365_2026.pdf",
    "nextias_ca":        ECONOMY_DIR / "Next IAS_ECO current affairs .pdf",
}

# Keywords to search for — each maps to a label
KEYWORDS = [
    # Monetary policy
    (["repo rate", "policy rate", "rbi rate"], "REPO RATE"),
    (["reverse repo", "srdf", "sdf rate", "standing deposit"], "SDF/REVERSE REPO"),
    (["crr", "cash reserve ratio"], "CRR"),
    (["slr", "statutory liquidity"], "SLR"),
    (["mpc", "monetary policy committee", "inflation target"], "MPC/INFLATION TARGET"),
    # Macro indicators
    (["gdp growth", "real gdp", "gross domestic product"], "GDP GROWTH"),
    (["gva", "gross value added"], "GVA"),
    (["cpi", "consumer price index", "retail inflation", "headline inflation"], "CPI INFLATION"),
    (["wpi", "wholesale price"], "WPI"),
    (["iip", "industrial production"], "IIP"),
    # Fiscal
    (["fiscal deficit", "gfd", "gross fiscal deficit"], "FISCAL DEFICIT"),
    (["revenue deficit"], "REVENUE DEFICIT"),
    (["primary deficit"], "PRIMARY DEFICIT"),
    (["capital expenditure", "capex"], "CAPITAL EXPENDITURE"),
    (["disinvestment", "divestment"], "DISINVESTMENT"),
    (["frbm", "fiscal responsibility"], "FRBM"),
    (["market borrowing", "gross borrowing"], "MARKET BORROWING"),
    # External
    (["current account deficit", "cad"], "CURRENT ACCOUNT DEFICIT"),
    (["forex reserve", "foreign exchange reserve", "foreign currency reserve"], "FOREX RESERVES"),
    (["fdi", "foreign direct investment"], "FDI"),
    (["rupee", "usd", "exchange rate", "inr"], "EXCHANGE RATE"),
    (["export", "import", "trade deficit", "trade balance"], "TRADE"),
    # Banking
    (["npa", "non-performing", "bad loan", "stressed asset"], "NPA"),
    (["credit growth", "bank credit"], "CREDIT GROWTH"),
    (["crar", "capital adequacy"], "CRAR"),
    # Inclusion / schemes
    (["jan dhan", "pmjdy", "jandhan"], "JAN DHAN"),
    (["mudra", "pmmy"], "MUDRA"),
    (["upi", "unified payment"], "UPI"),
    (["plfs", "labour force", "unemployment", "lfpr"], "EMPLOYMENT/UNEMPLOYMENT"),
]


def extract_text(pdf_path: Path, max_pages: int = 80) -> str:
    """Extract plain text from a PDF via pdftotext."""
    if not pdf_path.exists():
        return f"[FILE NOT FOUND: {pdf_path.name}]"
    try:
        result = subprocess.run(
            ["pdftotext", "-l", str(max_pages), str(pdf_path), "-"],
            capture_output=True, text=True, timeout=60,
        )
        return result.stdout
    except Exception as e:
        return f"[ERROR reading {pdf_path.name}: {e}]"


def find_snippets(text: str, keywords: list[str], context: int = 180) -> list[str]:
    """Return up to 3 snippets where any keyword appears."""
    text_lower = text.lower()
    snippets = []
    seen_positions = []

    for kw in keywords:
        start = 0
        while True:
            idx = text_lower.find(kw, start)
            if idx == -1:
                break
            # Avoid duplicate overlapping snippets
            if not any(abs(idx - s) < context for s in seen_positions):
                snippet_start = max(0, idx - 60)
                snippet_end = min(len(text), idx + context)
                raw = text[snippet_start:snippet_end].replace("\n", " ").strip()
                # Collapse whitespace
                raw = re.sub(r" {2,}", " ", raw)
                snippets.append(f"  …{raw}…")
                seen_positions.append(idx)
                if len(snippets) >= 3:
                    return snippets
            start = idx + 1

    return snippets


def main():
    out_lines = ["=" * 70, "RBI DEPR DATA EXTRACT — from UPSC Economy PDFs", "=" * 70, ""]

    corpus: dict[str, str] = {}
    for key, path in PDFS.items():
        print(f"Reading {path.name}…", file=sys.stderr)
        corpus[key] = extract_text(path)

    # Combined text for broad search
    combined = "\n\n".join(f"[{k}]\n{v}" for k, v in corpus.items())

    for kw_group, label in KEYWORDS:
        snippets = find_snippets(combined, kw_group)
        if snippets:
            out_lines.append(f"── {label} {'─' * (50 - len(label))}")
            out_lines.extend(snippets)
            out_lines.append("")

    # Per-file summary (first 120 chars of each page for Budget/Survey)
    out_lines += ["", "=" * 70, "BUDGET 2026 — FIRST 15 PAGES (for manual scan)", "=" * 70]
    for key in ["budget_highlights", "budget_analysis"]:
        path = PDFS[key]
        if not path.exists():
            continue
        out_lines.append(f"\n── {path.name} ──")
        text = extract_text(path, max_pages=15)
        out_lines.append(text[:4000])

    output = "\n".join(out_lines)
    out_path = Path(__file__).parent.parent / "data" / "rbi_current_data.txt"
    out_path.write_text(output, encoding="utf-8")
    print(f"Written: {out_path} ({len(output):,} chars)", file=sys.stderr)
    print(output[:3000])  # preview


if __name__ == "__main__":
    main()
