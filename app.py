import io
import json
import time
import html
from pathlib import Path

import streamlit as st
from PIL import Image

from core.config import GEMINI_API_KEY, GEMINI_MODEL, APP_NAME, APP_VERSION
from agents.vision_agent import run_vision_extraction
from agents.safety_agent import run_safety_audit
from agents.liaison_agent import run_patient_liaison
from core.pdf_generator import generate_patient_pdf


st.set_page_config(
    page_title="EchoCare AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----------------------------- PREMIUM DESIGN SYSTEM -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

:root{
  --bg:#FFFFFF;
  --surface:#FFFFFF;
  --surface2:#FCFAFB;
  --line:rgba(105,16,48,.13);
  --muted:#76636A;
  --text:#28161D;
  --purple:#76183A;
  --purple2:#9A4966;
  --blue:#76183A;
  --cyan:#8E3155;
  --green:#287A58;
  --amber:#A86D20;
  --red:#9E2348;
}
html,body,[class*="css"],.stApp{
  font-family:'DM Sans',sans-serif!important;
  background:
    radial-gradient(circle at 15% 0%,rgba(118,24,58,.08),transparent 32%),
    radial-gradient(circle at 90% 12%,rgba(154,73,102,.06),transparent 28%),
    var(--bg)!important;
  color:var(--text)!important;
}
header,footer{visibility:hidden!important}
.block-container{max-width:1480px!important;padding-top:2rem!important;padding-bottom:4rem!important}
.stApp:before{
 content:"";position:fixed;inset:0;pointer-events:none;opacity:.23;
 background-image:linear-gradient(rgba(118,24,58,.025) 1px,transparent 1px),linear-gradient(90deg,rgba(118,24,58,.025) 1px,transparent 1px);
 background-size:48px 48px;mask-image:linear-gradient(to bottom,#000,transparent 78%);
}

/* Splash */
#ec-splash{
 position:fixed;inset:0;z-index:999999;background:#FFFFFF;
 display:flex;align-items:center;justify-content:center;
 animation:ecSplash 1.0s ease 2.1s forwards;pointer-events:none;
}
.ec-splash-inner{text-align:center;animation:ecRise 1.2s ease}
.ec-logo{
 width:112px;height:112px;border-radius:34px;display:grid;place-items:center;margin:auto;
 background:linear-gradient(145deg,#76183A,#541128);
 border:1px solid rgba(118,24,58,.28);
 box-shadow:0 0 0 8px rgba(118,24,58,.04),0 0 80px rgba(118,24,58,.20);
}
.ec-logo svg{width:66px;height:66px}
.ec-brand{font:800 36px Manrope,sans-serif;letter-spacing:-1.8px;margin-top:22px}
.ec-brand span{color:#76183A}
.ec-sub{font-size:12px;letter-spacing:3px;color:#76636A;text-transform:uppercase;margin-top:7px}
.ec-load{width:190px;height:3px;background:#E8DCE1;border-radius:20px;margin:28px auto 0;overflow:hidden}
.ec-load i{display:block;width:100%;height:100%;background:linear-gradient(90deg,#76183A,#9A4966);transform:translateX(-100%);animation:ecLoad 2s cubic-bezier(.65,0,.35,1) forwards}
@keyframes ecSplash{to{opacity:0;visibility:hidden}}
@keyframes ecRise{from{opacity:0;transform:translateY(16px) scale(.97)}to{opacity:1;transform:none}}
@keyframes ecLoad{to{transform:translateX(0)}}

/* Header */
.ec-header{display:flex;align-items:center;justify-content:space-between;padding:6px 0 24px}
.ec-brandrow{display:flex;gap:13px;align-items:center}
.ec-mini-logo{width:48px;height:48px;border-radius:15px;background:linear-gradient(145deg,#76183A,#541128);border:1px solid rgba(118,24,58,.22);display:grid;place-items:center;box-shadow:0 8px 28px rgba(0,0,0,.3)}
.ec-mini-logo svg{width:29px;height:29px}
.ec-title{font:800 25px Manrope,sans-serif;letter-spacing:-.7px}
.ec-title span{color:#76183A}
.ec-subtitle{color:#76636A;font-size:12px;margin-top:2px}
.ec-live{display:flex;align-items:center;gap:8px;border:1px solid rgba(40,122,88,.20);background:rgba(40,122,88,.06);padding:8px 12px;border-radius:999px;color:#287A58;font-size:11px;font-weight:700;letter-spacing:.7px}
.ec-dot{width:7px;height:7px;background:#36D399;border-radius:50%;box-shadow:0 0 12px #36D399}

/* Hero */
.hero{padding:29px 32px;border:1px solid var(--line);border-radius:26px;background:linear-gradient(120deg,#FFFFFF,#FCF8FA);box-shadow:0 25px 80px rgba(91,25,48,.10);position:relative;overflow:hidden;margin-bottom:22px}
.hero:after{content:"";position:absolute;width:330px;height:330px;right:-150px;top:-190px;border-radius:50%;background:rgba(118,24,58,.08);filter:blur(5px)}
.hero-kicker{color:#76183A;font-size:11px;font-weight:800;letter-spacing:2.2px;text-transform:uppercase}
.hero h1{font:800 35px Manrope,sans-serif;letter-spacing:-1.7px;margin:8px 0 7px;color:#28161D}
.hero p{color:#705F66;max-width:720px;margin:0;font-size:14px;line-height:1.7}
.hero-tags{display:flex;gap:8px;flex-wrap:wrap;margin-top:18px}
.tag{padding:6px 10px;border:1px solid rgba(118,24,58,.10);background:rgba(118,24,58,.025);border-radius:999px;font-size:10px;color:#634D55;font-weight:700}

/* Panels */
 .panel{background:#FFFFFF;border:1px solid var(--line);border-radius:22px;padding:22px;box-shadow:0 18px 55px rgba(91,25,48,.08);height:100%}
.panel-head{color:#28161D;display:flex;align-items:center;justify-content:space-between;margin-bottom:15px}
.panel-title{font:700 16px Manrope,sans-serif;color:#28161D}
.panel-sub{font-size:11px;color:#78859B;margin-top:3px}
.step{display:inline-flex;align-items:center;justify-content:center;width:25px;height:25px;border-radius:9px;background:rgba(118,24,58,.08);color:#76183A;font-size:11px;font-weight:800;margin-right:9px;border:1px solid rgba(118,24,58,.22)}
.status-chip{font-size:9px;text-transform:uppercase;letter-spacing:1px;font-weight:800;padding:6px 9px;border-radius:999px;background:rgba(142,49,85,.07);border:1px solid rgba(142,49,85,.15);color:#8E3155}

/* Uploader */
[data-testid="stFileUploader"]{border:1px dashed rgba(118,24,58,.24);border-radius:17px;padding:6px;background:rgba(118,24,58,.025)}
[data-testid="stFileUploaderDropzone"]{background:#FFFFFF!important;border-radius:13px!important}
.hud{position:relative;border-radius:18px;overflow:hidden;border:1px solid rgba(118,24,58,.20);background:#FFFFFF}
.hud:before,.hud:after{content:"";position:absolute;inset:14px;pointer-events:none;border:1px solid rgba(255,255,255,.06);z-index:3}
.hud:after{inset:22px;border-color:rgba(118,24,58,.14)}
.laser{position:absolute;left:7%;right:7%;height:2px;background:linear-gradient(90deg,transparent,#76183A,#8E3155,transparent);box-shadow:0 0 18px #76183A;z-index:4;animation:scan 2.5s ease-in-out infinite}
@keyframes scan{0%{top:5%}50%{top:94%}100%{top:5%}}
.empty-scan{text-align:center;padding:62px 20px;border:1px dashed rgba(255,255,255,.08);border-radius:17px;background:rgba(255,255,255,.012)}
.empty-icon{font-size:32px;opacity:.75}.empty-title{font-weight:700;margin-top:9px}.empty-sub{font-size:11px;color:#7D6B72;margin-top:5px}

/* Inputs/buttons */
.stTextArea textarea,.stTextInput input{
 background:#FFFFFF!important;border:1px solid rgba(255,255,255,.08)!important;color:#28161D!important;border-radius:12px!important;
}
.stButton>button,.stDownloadButton>button{
 border:1px solid rgba(118,24,58,.28)!important;border-radius:12px!important;
 background:linear-gradient(135deg,#76183A,#8E3155)!important;color:#FFFFFF!important;
 font-weight:800!important;min-height:46px!important;box-shadow:0 10px 28px rgba(91,82,220,.22)!important;transition:.22s!important
}
.stButton>button:hover,.stDownloadButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 16px 35px rgba(91,82,220,.34)!important}
.stButton>button:disabled{opacity:.45!important}
label{color:#634D55!important;font-size:12px!important;font-weight:600!important}
.stCaption,.stMarkdown p{color:#705F66}
div[data-baseweb="tab-list"]{gap:4px;background:#FBF8F9;padding:5px;border-radius:14px;border:1px solid var(--line)}
button[data-baseweb="tab"]{border-radius:10px!important;color:#76636A!important;font-weight:700!important}
button[data-baseweb="tab"][aria-selected="true"]{background:#F3E8EC!important;color:#76183A!important}
div[data-testid="stStatusWidget"]{background:#FFFFFF!important;border:1px solid var(--line)!important;border-radius:16px!important}

/* Cards */
.med-card{padding:15px 16px;margin:10px 0;border:1px solid rgba(255,255,255,.07);border-radius:15px;background:linear-gradient(135deg,#FFFFFF,#FBF8F9);border-left:3px solid #76183A}
.med-top{display:flex;justify-content:space-between;gap:10px;align-items:center}.med-name{font-weight:800;font-size:14px}.confidence{font-size:9px;text-transform:uppercase;letter-spacing:.7px;padding:4px 7px;border-radius:99px;font-weight:800}
.meta{font-size:11px;color:#76636A;margin-top:7px;line-height:1.7}.meta b{color:#3C2B31}
.risk{padding:15px;border-radius:15px;border:1px solid;margin-bottom:13px}
.risk-low{background:rgba(40,122,88,.05);border-color:rgba(40,122,88,.22)}
.risk-mod{background:rgba(168,109,32,.05);border-color:rgba(168,109,32,.22)}
.risk-high{background:rgba(158,35,72,.05);border-color:rgba(158,35,72,.25)}
.risk-label{font-size:10px;font-weight:900;letter-spacing:1.2px}
.agent-row{display:flex;align-items:center;gap:11px;padding:11px 12px;border:1px solid rgba(255,255,255,.055);background:rgba(118,24,58,.025);border-radius:13px;margin:8px 0}
.agent-num{width:31px;height:31px;border-radius:10px;display:grid;place-items:center;background:rgba(118,24,58,.08);color:#76183A;font-weight:900;font-size:11px}
.agent-name{font-weight:800;font-size:12px}.agent-desc{font-size:10px;color:#7C6970;margin-top:2px}.agent-ok{margin-left:auto;color:#287A58;font-size:11px;font-weight:800}
.timeline{border-left:1px solid rgba(118,24,58,.3);margin:10px 0 4px 9px;padding-left:18px}
.slot{position:relative;padding:10px 0}.slot:before{content:"";position:absolute;left:-23px;top:14px;width:8px;height:8px;border-radius:50%;background:#76183A;box-shadow:0 0 10px rgba(118,24,58,.8)}
.slot-title{font-weight:800;font-size:12px}.slot-item{font-size:11px;color:#604F56;line-height:1.6;margin-top:4px}
.metric{background:#FCFAFB;border:1px solid rgba(255,255,255,.06);border-radius:15px;padding:13px}.metric-v{font:800 21px Manrope}.metric-l{font-size:9px;color:#806E75;text-transform:uppercase;letter-spacing:1px;margin-top:3px}
.footer-note{text-align:center;color:#8A767D;font-size:10px;margin-top:28px}
.disclaimer{padding:12px 14px;border:1px solid rgba(168,109,32,.18);background:rgba(168,109,32,.04);border-radius:12px;color:#66545B;font-size:10px;line-height:1.6}
@media(max-width:900px){.hero h1{font-size:28px}.ec-live{display:none}}
</style>

<div id="ec-splash">
  <div class="ec-splash-inner">
    <div class="ec-logo">
      <svg viewBox="0 0 100 100" fill="none">
        <path d="M50 78c-3-14-13-23-13-39a13 13 0 1 1 26 0c0 16-10 25-13 39Z" stroke="#fff" stroke-width="6" stroke-linecap="round"/>
        <path d="M50 27v28M36 41h28" stroke="#fff" stroke-width="6" stroke-linecap="round"/>
      </svg>
    </div>
    <div class="ec-brand">EchoCare <span>AI</span></div>
    <div class="ec-sub">Clinical intelligence, made understandable</div>
    <div class="ec-load"><i></i></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ----------------------------- HELPERS -----------------------------
def esc(value) -> str:
    return html.escape(str(value or ""))

def save_result(extraction, safety, plan):
    st.session_state.result = {
        "extraction": extraction,
        "safety": safety,
        "plan": plan,
        "created_at": time.strftime("%Y-%m-%d %H:%M"),
    }

def clear_result():
    st.session_state.pop("result", None)

def render_agent_telemetry():
    st.markdown("""
    <div class="agent-row"><div class="agent-num">01</div><div><div class="agent-name">Vision & OCR Specialist</div><div class="agent-desc">Multimodal handwriting extraction + confidence tagging</div></div><div class="agent-ok">READY</div></div>
    <div class="agent-row"><div class="agent-num">02</div><div><div class="agent-name">Clinical Safety Auditor</div><div class="agent-desc">Interaction + patient-context safety screening</div></div><div class="agent-ok">READY</div></div>
    <div class="agent-row"><div class="agent-num">03</div><div><div class="agent-name">Bilingual Patient Liaison</div><div class="agent-desc">Plain English + Roman Urdu routine synthesis</div></div><div class="agent-ok">READY</div></div>
    """, unsafe_allow_html=True)

def render_medications(extraction):
    st.markdown(f"**Patient:** `{esc(extraction.patient_name or 'Not specified')}`")
    if extraction.doctor_notes:
        st.info(f"**Extraction notes:** {extraction.doctor_notes}")
    if not extraction.medications:
        st.warning("No medication entities were extracted. Review the image and try a clearer scan.")
        return
    for idx, med in enumerate(extraction.medications, 1):
        c = str(med.confidence).lower()
        color = "#36D399" if c == "high" else "#FFB84D" if c == "medium" else "#FF5D73"
        st.markdown(f"""
        <div class="med-card">
          <div class="med-top"><div class="med-name">{idx}. {esc(med.name)} <span style="color:#7C879A">·</span> {esc(med.dosage)}</div>
          <div class="confidence" style="color:{color};border:1px solid {color}44;background:{color}0D">OCR {esc(med.confidence)}</div></div>
          <div class="meta">Timing <b>{esc(med.timing)}</b> &nbsp;·&nbsp; Frequency <b>{esc(med.frequency)}</b> &nbsp;·&nbsp; Duration <b>{esc(med.duration)}</b></div>
        </div>
        """, unsafe_allow_html=True)

def render_safety(safety):
    risk = str(safety.risk_score).lower()
    cls = "risk-high" if risk in ("severe","critical","high") else "risk-mod" if risk == "moderate" else "risk-low"
    accent = "#FF5D73" if "high" in cls else "#FFB84D" if "mod" in cls else "#36D399"
    st.markdown(f"""
    <div class="risk {cls}">
      <div class="risk-label" style="color:{accent}">SAFETY SCREEN · {esc(safety.risk_score).upper()}</div>
      <div style="font-size:12px;color:#4D3B42;margin-top:6px;line-height:1.6">{esc(safety.general_guidance)}</div>
    </div>
    """, unsafe_allow_html=True)
    if safety.conflicts:
        for conflict in safety.conflicts:
            st.markdown(f"""
            <div class="med-card" style="border-left-color:#9E2348">
              <div class="med-name" style="color:#9E2348">{esc(conflict.severity)} · {esc(", ".join(conflict.drugs_involved))}</div>
              <div class="meta"><b>Why:</b> {esc(conflict.explanation)}</div>
              <div class="meta"><b>Verification:</b> {esc(conflict.recommendation)}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("No potential conflict was identified from the supplied information. This is a screening result, not a guarantee of safety.")
    st.markdown('<div class="disclaimer">⚕️ EchoCare AI does not diagnose, prescribe, or authorize medication changes. Confirm any warning, dosage, allergy, or interaction with a qualified healthcare professional.</div>', unsafe_allow_html=True)

def render_timeline(slots):
    st.markdown('<div class="timeline">', unsafe_allow_html=True)
    for slot in slots:
        items = "".join(f'<div class="slot-item">• {esc(item)}</div>' for item in slot.action_items)
        st.markdown(f'<div class="slot"><div class="slot-title">{esc(slot.time_window)}</div>{items}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------- HEADER -----------------------------
st.markdown("""
<div class="ec-header">
  <div class="ec-brandrow">
    <div class="ec-mini-logo">
      <svg viewBox="0 0 100 100" fill="none"><path d="M50 78c-3-14-13-23-13-39a13 13 0 1 1 26 0c0 16-10 25-13 39Z" stroke="#76183A" stroke-width="6" stroke-linecap="round"/><path d="M50 27v28M36 41h28" stroke="#fff" stroke-width="6" stroke-linecap="round"/></svg>
    </div>
    <div><div class="ec-title">EchoCare <span>AI</span></div><div class="ec-subtitle">Multimodal Clinical Safety Copilot · v2.0</div></div>
  </div>
  <div class="ec-live"><span class="ec-dot"></span> GEMINI CORE ONLINE</div>
</div>
<div class="hero">
  <div class="hero-kicker">Autonomous agent intelligence</div>
  <h1>From prescription image to patient-ready clarity.</h1>
  <p>EchoCare AI coordinates three specialized agents to extract medication instructions, screen for potential safety conflicts, and turn complex prescriptions into accessible English and Roman Urdu routines.</p>
  <div class="hero-tags"><span class="tag">VISION OCR</span><span class="tag">SAFETY SCREEN</span><span class="tag">BILINGUAL CARE</span><span class="tag">PDF EXPORT</span><span class="tag">VOICE READY</span></div>
</div>
""", unsafe_allow_html=True)

if not GEMINI_API_KEY:
    st.error("Gemini API key is missing. Add GEMINI_API_KEY to your local `.env` file or Streamlit secrets.")
    st.stop()

# ----------------------------- SESSION -----------------------------
if "result" not in st.session_state:
    st.session_state.result = None

# ----------------------------- WORKSPACE -----------------------------
left, right = st.columns([0.9, 1.25], gap="large")

with left:
    st.markdown("""
    <div class="panel">
      <div class="panel-head"><div><div class="panel-title"><span class="step">01</span>Prescription intake</div><div class="panel-sub">Securely provide the visual source for the agent swarm.</div></div><span class="status-chip">SCAN CONSOLE</span></div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Prescription image", type=["jpg","jpeg","png"], label_visibility="collapsed")
    image = None

    if uploaded_file:
        try:
            image = Image.open(uploaded_file).convert("RGB")
            st.markdown('<div class="hud"><div class="laser"></div>', unsafe_allow_html=True)
            st.image(image, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.caption(f"Loaded · {image.width} × {image.height}px · {uploaded_file.size/1024:.0f} KB")
        except Exception:
            st.error("The uploaded image could not be read.")
    else:
        st.markdown("""
        <div class="empty-scan">
          <div class="empty-icon">⌁</div><div class="empty-title">Awaiting prescription scan</div>
          <div class="empty-sub">JPG or PNG · clear, well-lit handwriting gives the best extraction quality</div>
        </div>
        """, unsafe_allow_html=True)

    patient_history = st.text_area(
        "Patient context · conditions / allergies",
        placeholder="Example: hypertension; type 2 diabetes; aspirin allergy; kidney disease",
        height=90,
    )

    b1, b2 = st.columns([1.7, 1])
    with b1:
        execute = st.button("✦  RUN ECHOCARE SWARM", use_container_width=True)
    with b2:
        if st.button("Reset", use_container_width=True):
            clear_result()
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="panel" style="margin-top:18px">
      <div class="panel-head"><div><div class="panel-title">Agent architecture</div><div class="panel-sub">Deterministic sequential handoff</div></div></div>
    """, unsafe_allow_html=True)
    render_agent_telemetry()
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown("""
    <div class="panel">
      <div class="panel-head"><div><div class="panel-title"><span class="step">02</span>Swarm command center</div><div class="panel-sub">Live orchestration, clinical screening, and patient communication.</div></div><span class="status-chip">TELEMETRY</span></div>
    """, unsafe_allow_html=True)

    if execute:
        if image is None:
            st.warning("Upload a prescription image first.")
        else:
            timings = {}
            try:
                with st.status("EchoCare swarm is coordinating…", expanded=True) as status:
                    t=time.perf_counter()
                    st.write("🔭 **Agent 01** · Reading prescription image and structuring medication entities…")
                    extraction=run_vision_extraction(image)
                    timings["Vision OCR"]=time.perf_counter()-t
                    st.write(f"🟢 Extracted **{len(extraction.medications)}** medication entities.")
                    t=time.perf_counter()
                    st.write("🛡️ **Agent 02** · Screening interactions and patient-context contraindication risks…")
                    safety=run_safety_audit(extraction, patient_history)
                    timings["Safety"]=time.perf_counter()-t
                    st.write(f"🛡️ Safety screening complete · **{str(safety.risk_score).upper()}** risk screen.")
                    t=time.perf_counter()
                    st.write("◌ **Agent 03** · Building bilingual patient-ready routine…")
                    plan=run_patient_liaison(extraction, safety)
                    timings["Liaison"]=time.perf_counter()-t
                    st.write("🗣️ English + Roman Urdu plan generated.")
                    status.update(label="Swarm workflow completed", state="complete", expanded=False)
                save_result(extraction,safety,plan)
                st.toast("EchoCare analysis completed", icon="🩺")
            except Exception as e:
                st.error(f"Pipeline error: {e}")
                st.stop()

    result=st.session_state.get("result")

    if result:
        extraction=result["extraction"]; safety=result["safety"]; plan=result["plan"]
        m1,m2,m3=st.columns(3)
        with m1:
            st.markdown(f'<div class="metric"><div class="metric-v">{len(extraction.medications)}</div><div class="metric-l">Medicines extracted</div></div>',unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric"><div class="metric-v">{len(safety.conflicts)}</div><div class="metric-l">Potential flags</div></div>',unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric"><div class="metric-v">{esc(safety.risk_score).title()}</div><div class="metric-l">Risk screen</div></div>',unsafe_allow_html=True)

        tab1,tab2,tab3,tab4=st.tabs(["Medication map","Safety intelligence","Daily routine","Export & share"])
        with tab1:
            render_medications(extraction)
        with tab2:
            render_safety(safety)
        with tab3:
            language=st.radio("Routine language",["Roman Urdu","English"],horizontal=True,label_visibility="collapsed")
            if language=="Roman Urdu":
                st.markdown("#### Rozana dawa ka routine")
                render_timeline(plan.daily_schedule_roman_urdu)
                st.markdown("#### Parhez aur hidayat")
                for a in plan.dietary_advice_roman_urdu: st.markdown(f"• {a}")
                if plan.emergency_warning_roman_urdu: st.warning(plan.emergency_warning_roman_urdu)
                speech_text=" ".join([slot.time_window+". "+" ".join(slot.action_items) for slot in plan.daily_schedule_roman_urdu])
            else:
                st.markdown("#### Daily medication routine")
                render_timeline(plan.daily_schedule_en)
                st.markdown("#### Dietary guidance")
                for a in plan.dietary_advice_en: st.markdown(f"• {a}")
                speech_text=" ".join([slot.time_window+". "+" ".join(slot.action_items) for slot in plan.daily_schedule_en])

            # Browser-native voice; no server audio dependency.
            speech_json=json.dumps(speech_text)
            st.markdown(f"""
            <button id="ecSpeak" style="margin-top:8px;padding:10px 14px;border-radius:11px;border:1px solid rgba(118,24,58,.28);background:#F3E8EC;color:#76183A;font-weight:800;cursor:pointer">🔊 Read routine aloud</button>
            <script>
            const btn=document.getElementById("ecSpeak");
            if(btn) btn.onclick=()=>{{window.speechSynthesis.cancel();let u=new SpeechSynthesisUtterance({speech_json});u.rate=.92;window.speechSynthesis.speak(u);}};
            </script>
            """,unsafe_allow_html=True)
        with tab4:
            st.markdown("#### Patient-ready outputs")
            pdf_bytes=generate_patient_pdf(extraction,safety,plan)
            st.download_button("↓  Download clinical summary PDF",pdf_bytes,"EchoCare_Patient_Summary.pdf","application/pdf",use_container_width=True)
            export={
                "product":"EchoCare AI","version":APP_VERSION,"generated_at":result["created_at"],
                "prescription":extraction.model_dump(),"safety_screen":safety.model_dump(),"patient_plan":plan.model_dump()
            }
            st.download_button("↓  Export structured JSON",json.dumps(export,indent=2,ensure_ascii=False).encode(),"EchoCare_Analysis.json","application/json",use_container_width=True)
            st.markdown('<div class="disclaimer" style="margin-top:14px">🔐 The app does not need to store raw prescription audio or other unnecessary patient media. Treat generated reports as sensitive health information and share only through appropriate channels.</div>',unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="padding:55px 18px;text-align:center">
          <div style="font-size:36px;color:#76183A">◈</div>
          <div style="font:800 16px Manrope;margin-top:12px">Swarm standing by</div>
          <div style="font-size:11px;color:#7D6B72;max-width:430px;margin:7px auto;line-height:1.7">Upload a prescription and launch the swarm. The command center will reveal each agent handoff and the resulting clinical-safety and patient-education layers.</div>
        </div>
        """,unsafe_allow_html=True)

    st.markdown('</div>',unsafe_allow_html=True)

st.markdown('<div class="footer-note">EchoCare AI · v2.0 · AI-assisted prescription understanding · Always verify medication decisions with a qualified healthcare professional.</div>',unsafe_allow_html=True)
