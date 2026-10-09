
# ============================================================
# MAMAEARTH DATA ANALYST CAPSTONE PROJECT
# PART 3 - GENAI SCR BUSINESS NARRATIVE
# ============================================================

import os
import json
import re
from pathlib import Path

from google import genai
from google.genai import types


# ------------------------------------------------------------
# STEP 1 - FILE PATHS AND GEMINI MODEL
# ------------------------------------------------------------

folder = Path(__file__).resolve().parent

findings_file = folder / "findings.json"
sample_file = folder / "sample_output.txt"

MODEL_NAME = "gemini-3.6-flash"


# ------------------------------------------------------------
# STEP 2 - LOAD VERIFIED FINDINGS FROM PYTHON ANALYSIS
# ------------------------------------------------------------

def load_findings():

    with open(findings_file, "r", encoding="utf-8") as file:
        findings = json.load(file)

    return findings


# ------------------------------------------------------------
# STEP 3 - PREPARE FACTS FROM FINDINGS.JSON
# ------------------------------------------------------------

def prepare_facts(findings):

    rates = findings["return_rate_by_payment"]
    risk = findings["highest_risk_segment"]
    peak = findings["true_peak_month"]
    january = findings["outlier_inflated_month"]

    facts = f"""
Raw revenue: INR {findings['raw_total_revenue_inr']:,.2f}
Cleaned revenue: INR {findings['cleaned_total_revenue_inr']:,.2f}
Duplicate reconciliation: INR {findings['duplicate_reconciliation_delta_inr']:,.2f}

CARD return rate: {rates['CARD']:.1f}%
UPI return rate: {rates['UPI']:.1f}%
COD return rate: {rates['COD']:.1f}%

Highest-risk segment: {risk['payment_method']} in Tier {risk['city_tier']} cities
Highest-risk return rate: {risk['return_rate_pct']:.1f}%

True peak month: {peak['month']}
True peak revenue: INR {peak['revenue_inr']:,.2f}

January apparent revenue: INR {january['apparent_revenue_inr']:,.2f}
January corrected revenue: INR {january['corrected_revenue_inr']:,.2f}
"""

    return facts.strip()


# ------------------------------------------------------------
# STEP 4 - GENERATE SCR NARRATIVE USING GEMINI API
# ------------------------------------------------------------

def generate_scr_narrative(findings: dict) -> dict:

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:

        return {
            "status": "error",
            "narrative": None,
            "message": "GEMINI_API_KEY is missing"
        }

    facts = prepare_facts(findings)

    # Separate system instruction
    system_instruction = """
You are a business analyst working on Mamaearth's
Growth Analytics team.

Write a professional but easy-to-understand report
for regional operations and finance leaders.

Use exactly three headings:
Situation
Complication
Resolution

Only use the verified facts provided.
Do not invent numbers, causes, or conclusions.

Important:
The duplicate reconciliation difference comes
from duplicate orders.

The January revenue correction comes from
quantity outliers.

These are two separate data quality issues.

Return only the final business report.
Do not repeat the instructions.
"""

    # User prompt using verified Python findings
    prompt = f"""
Write the final Situation-Complication-Resolution
(SCR) business narrative for Mamaearth.

VERIFIED FINDINGS:

{facts}

ADDITIONAL VERIFIED JSON:

{json.dumps(findings, indent=2)}

REQUIREMENTS:

Situation:
Explain the raw revenue, cleaned revenue
and true peak month.

Complication:
Explain the duplicate order reconciliation,
COD return rates, Tier 2 COD risk and
January's quantity outliers.

Resolution:
Recommend practical actions for operations
and finance.

Use the exact numerical values provided.
Format currency to two decimal places.
Format return rates to one decimal place.

Use these headings on separate lines:

Situation

Complication

Resolution

Start immediately with Situation.
Do not include planning notes or instructions.
"""

    try:

        with genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=60000)
        ) as client:

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.0,
                    max_output_tokens=4096
                )
            )

        narrative = response.text

        if not narrative or not narrative.strip():
            raise ValueError("Gemini returned an empty response")

        usage = response.usage_metadata

        tokens = (
            usage.total_token_count
            if usage is not None
            else None
        )

        return {
            "status": "success",
            "narrative": narrative.strip(),
            "tokens": tokens
        }

    except Exception as error:

        return {
            "status": "error",
            "narrative": None,
            "message": str(error)
        }


# ------------------------------------------------------------
# STEP 5 - OFFLINE SCR FALLBACK
# ------------------------------------------------------------

def generate_scr_narrative_offline(findings: dict) -> dict:

    raw = findings["raw_total_revenue_inr"]
    clean = findings["cleaned_total_revenue_inr"]
    delta = findings["duplicate_reconciliation_delta_inr"]

    rates = findings["return_rate_by_payment"]
    risk = findings["highest_risk_segment"]
    peak = findings["true_peak_month"]
    january = findings["outlier_inflated_month"]

    narrative = f"""
Situation

Mamaearth recorded raw revenue of INR {raw:,.2f}.
After removing duplicate orders, cleaned revenue
was INR {clean:,.2f}.

The true peak month after outlier correction was
{peak['month']}, with revenue of
INR {peak['revenue_inr']:,.2f}.

Complication

Duplicate orders inflated revenue by INR {delta:,.2f}.

COD recorded a return rate of {rates['COD']:.1f}%,
compared with CARD at {rates['CARD']:.1f}%
and UPI at {rates['UPI']:.1f}%.

The highest-risk segment was COD in Tier
{risk['city_tier']} cities, with a return rate
of {risk['return_rate_pct']:.1f}%.

January 2026 initially showed revenue of
INR {january['apparent_revenue_inr']:,.2f}.
After removing quantity outliers, the corrected
January revenue was
INR {january['corrected_revenue_inr']:,.2f}.

The duplicate reconciliation and quantity outlier
correction are separate data quality issues.

Resolution

Operations should investigate COD returns,
especially in Tier 2 cities.

The team should review return reasons,
improve delivery confirmation and encourage
prepaid payments where appropriate.

Finance should use cleaned revenue figures
for reporting and investigate unusual bulk orders.

Monthly revenue comparisons should use
outlier-corrected figures to avoid misleading
business conclusions.
""".strip()

    return {
        "status": "success",
        "narrative": narrative,
        "tokens": 0
    }


# ------------------------------------------------------------
# STEP 6 - VALIDATE NUMERIC RESULTS AND SCR HEADINGS
# ------------------------------------------------------------

def validate_narrative(findings: dict, narrative: str) -> bool:

    # Remove commas for numeric comparisons
    text = narrative.replace(",", "")

    clean = findings["cleaned_total_revenue_inr"]
    delta = findings["duplicate_reconciliation_delta_inr"]

    cod = findings["return_rate_by_payment"]["COD"]
    risk = findings["highest_risk_segment"]["return_rate_pct"]
    peak = findings["true_peak_month"]["revenue_inr"]

    numeric_checks = {
        "Cleaned revenue":
            f"{clean:.2f}" in text,

        "COD return rate":
            f"{cod:.1f}%" in text,

        "COD Tier 2 return rate":
            f"{risk:.1f}%" in text,

        "Duplicate reconciliation":
            f"{delta:.2f}" in text,

        "March peak revenue":
            f"{peak:.2f}" in text
            and (
                "March 2026" in narrative
                or "2026-03" in narrative
            )
    }

    print("\nNUMERIC VALIDATION RESULTS")
    print("-" * 45)

    for name, passed in numeric_checks.items():

        status = "PASS" if passed else "FAIL"
        print(f"{status} - {name}")

    # Check SCR headings without complicated regular expressions
    headings = ["Situation", "Complication", "Resolution"]

    lines = [
        line.strip().replace("#", "").strip().rstrip(":").strip()
        for line in narrative.splitlines()
    ]

    heading_checks = {
        heading: heading in lines
        for heading in headings
    }

    print("\nSCR STRUCTURE VALIDATION")
    print("-" * 45)

    for heading, passed in heading_checks.items():

        status = "PASS" if passed else "FAIL"
        print(f"{status} - {heading}")

    return (
        all(numeric_checks.values())
        and all(heading_checks.values())
    )


# ------------------------------------------------------------
# STEP 7 - MAIN PROGRAM
# ------------------------------------------------------------

def main():

    print("=" * 55)
    print("MAMAEARTH - PART 3 GENAI NARRATIVE")
    print("=" * 55)

    print("\nReading findings.json...")

    try:
        findings = load_findings()

    except Exception as error:
        print("Unable to load findings.json:", error)
        return

    print("Generating SCR narrative using Gemini...")

    result = generate_scr_narrative(findings)

    if result["status"] == "success":

        print("Gemini generation successful.")
        source = "Gemini"

    else:

        print("Gemini unavailable:", result["message"])
        print("Using automatic offline fallback...")

        result = generate_scr_narrative_offline(findings)
        source = "Offline"

    narrative = result["narrative"]

    print("\n" + narrative)

    valid = validate_narrative(findings, narrative)

    # Save only genuine validated Gemini output
    if source == "Gemini" and valid:

        sample_file.write_text(
            narrative,
            encoding="utf-8"
        )

        print("\nVerified Gemini sample saved:")
        print(sample_file)

        # Recheck the saved sample
        print("\nVALIDATING SAVED GEMINI SAMPLE")

        saved_narrative = sample_file.read_text(
            encoding="utf-8"
        )

        valid = validate_narrative(
            findings,
            saved_narrative
        )

    elif source == "Gemini" and not valid:

        print("\nGemini output failed validation.")
        print("Switching to offline fallback...")

        result = generate_scr_narrative_offline(findings)

        narrative = result["narrative"]
        source = "Offline"

        print("\nOFFLINE NARRATIVE:\n")
        print(narrative)

        valid = validate_narrative(
            findings,
            narrative
        )

        print("\nExisting Gemini sample was not overwritten.")

    else:

        print("\nOffline fallback completed.")
        print("Existing Gemini sample was not overwritten.")

    print("\nFinal narrative source:", source)
    print("Final validation:", "PASS" if valid else "FAIL")
    print("Pipeline finished.")


if __name__ == "__main__":
    main()
