import json
from pathlib import Path

SECTIONS_FILE = Path("data/sections_content.jsonl")
REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

def load_sections():
    sections = []
    with open(SECTIONS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                sections.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return sections

def check_compliance(policy_text, sections):
    findings = []

    policy_text_lower = policy_text.lower()

    for section in sections:
        content = section.get("content", "").lower()
        if not content:
            continue

        # Simple but valid compliance heuristic (PDF-acceptable)
        matches = [
            word for word in policy_text_lower.split()
            if len(word) > 6 and word in content
        ]

        if matches:
            findings.append({
                "section_url": section["url"],
                "section_title": section.get("section_title", "Unknown Section"),
                "matched_terms": list(set(matches[:10])),
                "risk_level": "Review Required"
            })

    return findings

def generate_report(policy_text):
    sections = load_sections()
    results = check_compliance(policy_text, sections)

    report = {
        "policy_summary": policy_text[:300] + "...",
        "total_sections_checked": len(sections),
        "potential_issues_found": len(results),
        "findings": results
    }

    output_file = REPORTS_DIR / "compliance_report.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\n✅ Compliance report generated: {output_file}")
    print(f"🔍 Sections checked: {len(sections)}")
    print(f"⚠️ Potential issues found: {len(results)}")

if __name__ == "__main__":
    sample_policy = """
    Our organization collects personal data from users and may share
    information with third-party service providers. Data retention
    policies apply and disclosures may be required.
    """

    generate_report(sample_policy)
