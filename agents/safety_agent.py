import json
from google import genai
from google.genai import types
from core.schemas import PrescriptionExtraction, ClinicalSafetyReport
from core.config import GEMINI_API_KEY, GEMINI_MODEL


def run_safety_audit(
    extraction: PrescriptionExtraction,
    patient_history: str = ""
) -> ClinicalSafetyReport:
    """Agent 2: medication safety screening. Results require professional verification."""
    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = f"""
You are EchoCare AI's Clinical Safety Screening Agent.

Perform a conservative SAFETY SCREEN on the extracted medication list and the supplied
patient context. Check:
1. Potential drug-drug interactions.
2. Potential medication-condition contraindications or cautions.
3. Obvious dosage/administration anomalies only when the supplied data supports the concern.

Patient context:
{patient_history or "No patient conditions/allergies supplied."}

Extracted prescription:
{json.dumps(extraction.model_dump(), indent=2)}

Important rules:
- Do not diagnose.
- Do not prescribe.
- Do not tell a patient to start, stop, increase, decrease, or substitute a medicine.
- Do not claim that an interaction is definitively present when the evidence is uncertain.
- Clearly label potential concerns as requiring pharmacist/doctor verification.
- If OCR confidence is Low, treat that as an additional uncertainty.
- If no issue is identified, say "No issue identified from the supplied information" rather
  than claiming the prescription is medically safe.
"""
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ClinicalSafetyReport,
            temperature=0.15,
        ),
    )
    return ClinicalSafetyReport.model_validate_json(response.text)
