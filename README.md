# EchoCare AI — Premium Clinical Copilot

EchoCare AI is a multimodal, sequential three-agent clinical copilot demo:

1. Vision & OCR Specialist — extracts prescription entities with confidence tagging.
2. Clinical Safety Auditor — screens medication combinations and patient-context risks.
3. Bilingual Patient Liaison — creates plain-English and Roman Urdu patient routines.

## Premium UI

The current design system uses **Pure White + Burgundy** (`#76183A`) with a subtle purple undertone (`#9A4966`). The interface is intentionally clean, clinical, and presentation-ready.

## Run on Windows

Double-click `run_echocare.bat` or run:

```cmd
run_echocare.bat
```

The launcher uses a 300-second pip timeout and retries to tolerate slower package downloads.

## Environment

Copy `.env.example` to `.env` and add your Gemini API key:

```env
GEMINI_API_KEY=YOUR_KEY_HERE
GEMINI_MODEL=gemini-2.5-flash
```

Never commit a real API key.

## Safety

EchoCare AI is an assistive software prototype. Its outputs must be reviewed by a qualified healthcare professional. It must not independently diagnose, prescribe, stop medication, or authorize medication changes.
