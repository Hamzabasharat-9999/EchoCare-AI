from google import genai
from google.genai import types
from PIL import Image
from core.schemas import PrescriptionExtraction
from core.config import GEMINI_API_KEY, GEMINI_MODEL


def run_vision_extraction(image: Image.Image) -> PrescriptionExtraction:
    """Agent 1: multimodal prescription extraction with uncertainty-aware OCR."""
    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = """
You are EchoCare AI's Vision & Medical OCR Specialist.

Read the prescription image conservatively. Extract only information that is actually
visible or reasonably legible. Do NOT invent a medicine, dosage, frequency, duration,
patient name, or diagnosis.

For every medication:
- preserve the medicine/salt name as written when possible
- capture dosage strength
- capture frequency
- capture meal/timing instruction
- capture duration if visible
- assign High, Medium, or Low confidence

If handwriting is ambiguous, use Low confidence and describe the uncertainty in doctor_notes
instead of guessing. Expand common abbreviations only when the image makes their meaning clear.
This output is an extraction aid, not a prescription.
"""
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[image, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=PrescriptionExtraction,
            temperature=0.1,
        ),
    )
    return PrescriptionExtraction.model_validate_json(response.text)
