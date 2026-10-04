from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class MedicationItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str = Field(description="Name of the medicine or active ingredient exactly as visible")
    dosage: str = Field(description="Dosage strength, e.g. 500mg, 10ml")
    frequency: str = Field(description="Frequency, e.g. Twice daily, Once at night, TDS")
    timing: str = Field(description="Before food, after food, with food, or as written")
    duration: Optional[str] = Field(default="As prescribed", description="Duration in days or weeks")
    confidence: str = Field(description="High, Medium, or Low confidence in OCR transcription")


class PrescriptionExtraction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    patient_name: Optional[str] = Field(default="Unspecified")
    doctor_notes: Optional[str] = Field(default="")
    medications: List[MedicationItem] = Field(default_factory=list)


class SafetyConflict(BaseModel):
    model_config = ConfigDict(extra="ignore")
    severity: str = Field(description="Critical, Moderate, or Mild")
    drugs_involved: List[str] = Field(default_factory=list)
    explanation: str
    recommendation: str


class ClinicalSafetyReport(BaseModel):
    model_config = ConfigDict(extra="ignore")
    is_safe: bool
    risk_score: str = Field(description="Low, Moderate, or Severe")
    conflicts: List[SafetyConflict] = Field(default_factory=list)
    general_guidance: str


class DailySlot(BaseModel):
    model_config = ConfigDict(extra="ignore")
    time_window: str
    action_items: List[str] = Field(default_factory=list)


class BilingualPatientPlan(BaseModel):
    model_config = ConfigDict(extra="ignore")
    daily_schedule_en: List[DailySlot] = Field(default_factory=list)
    daily_schedule_roman_urdu: List[DailySlot] = Field(default_factory=list)
    dietary_advice_en: List[str] = Field(default_factory=list)
    dietary_advice_roman_urdu: List[str] = Field(default_factory=list)
    emergency_warning_roman_urdu: str = ""
