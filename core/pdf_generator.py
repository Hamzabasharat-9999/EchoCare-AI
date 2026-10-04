import io
import re
import unicodedata
from fpdf import FPDF
from core.schemas import PrescriptionExtraction, ClinicalSafetyReport, BilingualPatientPlan


# EchoCare uses FPDF's built-in Helvetica fonts so the PDF stays portable.
# AI-generated text can contain Unicode punctuation, emoji, Urdu characters,
# mathematical symbols, or very long tokens. These helpers normalize that text
# before it reaches fpdf2, preventing "Not enough horizontal space" crashes.
_UNICODE_REPLACEMENTS = str.maketrans({
    "\u2018": "'", "\u2019": "'", "\u201a": "'", "\u201b": "'",
    "\u201c": '"', "\u201d": '"', "\u201e": '"', "\u201f": '"',
    "\u2013": "-", "\u2014": "-", "\u2212": "-",
    "\u2026": "...", "\u2022": "-", "\u25cf": "-", "\u25a0": "-",
    "\u2192": "->", "\u2190": "<-", "\u2194": "<->",
    "\u2713": "[OK]", "\u2714": "[OK]", "\u2717": "[X]", "\u2718": "[X]",
    "\u00d7": "x", "\u00b0": " deg ", "\u00b1": "+/-",
    "\u00a0": " ", "\u200b": "", "\u200c": "", "\u200d": "",
})


def _pdf_text(value) -> str:
    """Return text that is safe for FPDF built-in Helvetica fonts."""
    text = "" if value is None else str(value)
    text = text.translate(_UNICODE_REPLACEMENTS)
    # Remove remaining control characters while preserving normal whitespace.
    text = "".join(ch if ch in "\n\r\t" or ord(ch) >= 32 else " " for ch in text)
    # Helvetica/WinAnsi cannot represent arbitrary Unicode. Replace anything
    # outside Windows-1252 rather than allowing fpdf2 to crash during encoding.
    text = text.encode("cp1252", errors="replace").decode("cp1252")
    # Break pathological unspaced tokens (URLs, IDs, generated hashes, etc.).
    # This is what prevents a single unbreakable token from exceeding the cell.
    text = re.sub(r"(\S{45})(?=\S)", r"\1 ", text)
    return text


def _multi(pdf: FPDF, text: str, h: float = 5) -> None:
    pdf.multi_cell(0, h, _pdf_text(text), wrapmode="WORD", new_x="LMARGIN", new_y="NEXT")


class RegimenPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(118, 24, 58)
        self.cell(0, 10, _pdf_text("EchoCare AI - Patient Medication Summary"),
                  border=False, new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(100, 85, 92)
        self.cell(0, 5, _pdf_text(
            "AI-assisted organization and safety screening - professional verification required"
        ), border=False, new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 105, 112)
        self.cell(
            0, 10,
            _pdf_text(
                f"Page {self.page_no()} | EchoCare AI is not a substitute for a qualified healthcare professional."
            ),
            align="C",
        )


def generate_patient_pdf(
    extraction: PrescriptionExtraction,
    safety: ClinicalSafetyReport,
    plan: BilingualPatientPlan,
) -> bytes:
    pdf = RegimenPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_title("EchoCare AI Patient Medication Summary")
    pdf.set_author("EchoCare AI")
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(118, 24, 58)
    pdf.cell(0, 8, _pdf_text("1. Extracted Prescription"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(35, 35, 40)
    pdf.cell(0, 6, _pdf_text(f"Patient: {extraction.patient_name or 'Not specified'}"),
              new_x="LMARGIN", new_y="NEXT")
    if extraction.doctor_notes:
        _multi(pdf, f"Notes: {extraction.doctor_notes}")
    pdf.ln(2)

    for idx, med in enumerate(extraction.medications, 1):
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(0, 5, _pdf_text(f"{idx}. {med.name} ({med.dosage})"),
                  new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        _multi(
            pdf,
            f"Timing: {med.timing} | Frequency: {med.frequency} | "
            f"Duration: {med.duration} | OCR confidence: {med.confidence}"
        )
        pdf.ln(1)

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(118, 24, 58)
    pdf.cell(0, 8, _pdf_text(f"2. Safety Screening - {safety.risk_score.upper()}"),
              new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(35, 35, 40)
    _multi(pdf, safety.general_guidance)

    for conflict in safety.conflicts:
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(
            0, 5,
            _pdf_text(f"{conflict.severity}: {', '.join(conflict.drugs_involved)}"),
            new_x="LMARGIN", new_y="NEXT",
        )
        pdf.set_font("Helvetica", "", 9)
        _multi(pdf, f"Concern: {conflict.explanation}")
        _multi(pdf, f"Verification: {conflict.recommendation}")

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(118, 24, 58)
    pdf.cell(0, 8, _pdf_text("3. Daily Routine - Roman Urdu"),
              new_x="LMARGIN", new_y="NEXT")
    for slot in plan.daily_schedule_roman_urdu:
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(0, 5, _pdf_text(slot.time_window), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        for item in slot.action_items:
            _multi(pdf, f"- {item}")

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, _pdf_text("Parhez / Dietary Guidance"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    for advice in plan.dietary_advice_roman_urdu:
        _multi(pdf, f"- {advice}")

    if plan.emergency_warning_roman_urdu:
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(0, 5, _pdf_text("Safety Warning"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        _multi(pdf, plan.emergency_warning_roman_urdu)

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 5, _pdf_text("Important"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    _multi(
        pdf,
        "This report is generated from the supplied prescription image and patient context. "
        "Confirm medicine names, doses, interactions, allergies, and instructions with a "
        "qualified doctor or pharmacist before making medication decisions."
    )

    output = io.BytesIO()
    pdf.output(output)
    return output.getvalue()
