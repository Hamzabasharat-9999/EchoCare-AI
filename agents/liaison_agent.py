import json
from google import genai
from google.genai import types
from core.schemas import PrescriptionExtraction, ClinicalSafetyReport, BilingualPatientPlan
from core.config import GEMINI_API_KEY, GEMINI_MODEL


def run_patient_liaison(
    extraction: PrescriptionExtraction,
    safety: ClinicalSafetyReport
) -> BilingualPatientPlan:
    """Agent 3: converts extracted instructions into accessible bilingual education."""
    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = f"""
You are EchoCare AI's Patient Care Liaison.

Create an easy-to-understand medication education plan from the extracted prescription.
Provide both plain English and natural Roman Urdu (Urdu written in Latin alphabet).

Medication data:
{json.dumps(extraction.model_dump(), indent=2)}

Safety screening:
{json.dumps(safety.model_dump(), indent=2)}

Requirements:
- Do not create new doses or change prescribed instructions.
- Keep uncertain/low-confidence items visibly uncertain.
- Organize instructions into Morning, Afternoon, Evening, and Bedtime where applicable.
- Include only practical dietary/administration reminders supported by the supplied data.
- Include a short emergency/safety reminder in Roman Urdu.
- The output is patient education and organization, not a replacement for a doctor's advice.
"""
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=BilingualPatientPlan,
            temperature=0.25,
        ),
    )
    return BilingualPatientPlan.model_validate_json(response.text)
