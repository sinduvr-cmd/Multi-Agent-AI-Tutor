"""
Custom CSS and High-Contrast Styling for Multi-Agent AI Tutor.
Ensures crystal-clear buttons, distinct multiple choice radio options,
readable sidebar navigation, and sleek dark mode inputs.
"""

CUSTOM_CSS = """
<style>
/* Modern Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Background & Main Container */
.stApp {
    background: linear-gradient(135deg, #090D16 0%, #0F172A 50%, #111827 100%);
    color: #F8FAFC !important;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background: #0B1120 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.12) !important;
}

[data-testid="stSidebar"] .stMarkdown h1, 
[data-testid="stSidebar"] .stMarkdown h2, 
[data-testid="stSidebar"] .stMarkdown h3,
[data-testid="stSidebar"] p {
    color: #F1F5F9 !important;
}

/* Sidebar Radio Navigation items - High Contrast & Sharp */
[data-testid="stSidebar"] div[role="radiogroup"] > label {
    background: rgba(30, 41, 59, 0.6) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 8px !important;
    padding: 8px 14px !important;
    margin-bottom: 6px !important;
    cursor: pointer !important;
    transition: all 0.15s ease-in-out !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    background: rgba(79, 70, 229, 0.25) !important;
    border-color: #818CF8 !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] > label p {
    color: #E2E8F0 !important;
    font-weight: 600 !important;
    font-size: 14px !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] > label:hover p {
    color: #FFFFFF !important;
}

/* ========================================================= */
/* BUTTONS: Crystal Clear, High Contrast, High Legibility    */
/* ========================================================= */

/* Secondary / Standard Buttons (Hint, Previous, Next, Finish, Flag, etc.) */
.stButton > button,
button[kind="secondary"] {
    background: #1E293B !important;
    color: #F8FAFC !important;
    border: 1.5px solid #475569 !important;
    border-radius: 10px !important;
    padding: 10px 18px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35) !important;
    transition: all 0.2s ease-in-out !important;
}

/* Ensure ALL text, spans, and icons inside secondary buttons are bright white */
.stButton > button *,
button[kind="secondary"] * {
    color: #F8FAFC !important;
    font-weight: 700 !important;
}

.stButton > button:hover,
button[kind="secondary"]:hover {
    background: #334155 !important;
    border-color: #38BDF8 !important;
    color: #38BDF8 !important;
    box-shadow: 0 4px 14px rgba(56, 189, 248, 0.25) !important;
    transform: translateY(-1px) !important;
}

.stButton > button:hover * {
    color: #38BDF8 !important;
}

/* Primary Buttons (Submit Answer, Generate Quiz, etc.) */
.stButton > button[kind="primary"],
button[kind="primary"] {
    background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
    color: #FFFFFF !important;
    border: 1.5px solid #34D399 !important;
    border-radius: 10px !important;
    padding: 10px 20px !important;
    font-weight: 800 !important;
    font-size: 15px !important;
    letter-spacing: 0.02em !important;
    box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4) !important;
    transition: all 0.2s ease-in-out !important;
}

.stButton > button[kind="primary"] *,
button[kind="primary"] * {
    color: #FFFFFF !important;
    font-weight: 800 !important;
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
    border-color: #6EE7B7 !important;
    box-shadow: 0 6px 18px rgba(16, 185, 129, 0.5) !important;
    transform: translateY(-1px) !important;
}

/* Disabled Button state */
.stButton > button:disabled,
button:disabled {
    background: #1E293B !important;
    color: #64748B !important;
    border-color: #334155 !important;
    box-shadow: none !important;
    cursor: not-allowed !important;
    opacity: 0.7 !important;
}

.stButton > button:disabled * {
    color: #64748B !important;
}

/* ========================================================= */
/* RADIO OPTIONS & MCQS: Bold, Clickable, High Contrast Cards*/
/* ========================================================= */

div[role="radiogroup"] {
    gap: 10px !important;
}

div[role="radiogroup"] > label {
    background: #1E293B !important;
    border: 1.5px solid #334155 !important;
    border-radius: 12px !important;
    padding: 12px 18px !important;
    margin-bottom: 10px !important;
    cursor: pointer !important;
    display: flex !important;
    align-items: center !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25) !important;
}

div[role="radiogroup"] > label:hover {
    background: #273549 !important;
    border-color: #6366F1 !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25) !important;
}

div[role="radiogroup"] > label p {
    color: #F8FAFC !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    line-height: 1.5 !important;
    margin: 0 !important;
}

/* Selected Radio State */
div[role="radiogroup"] > label[data-checked="true"],
div[role="radiogroup"] > label:has(input:checked) {
    background: rgba(79, 70, 229, 0.25) !important;
    border: 2px solid #818CF8 !important;
    box-shadow: 0 0 14px rgba(99, 102, 241, 0.4) !important;
}

div[role="radiogroup"] > label:has(input:checked) p {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

/* Radio button dot size & color */
div[role="radiogroup"] input[type="radio"] {
    accent-color: #818CF8 !important;
    width: 18px !important;
    height: 18px !important;
    margin-right: 12px !important;
}

/* ========================================================= */
/* TEXT INPUTS & TEXT AREAS: Dark, Sharp, Clean Contrast    */
/* ========================================================= */

.stTextInput input,
.stTextArea textarea {
    background: #1E293B !important;
    color: #FFFFFF !important;
    border: 1.5px solid #475569 !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
    font-size: 16px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2) !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: #38BDF8 !important;
    box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.25) !important;
    background: #243044 !important;
    outline: none !important;
}

.stTextInput label,
.stTextArea label {
    color: #CBD5E1 !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    margin-bottom: 6px !important;
}

/* Selectboxes & Dropdowns */
div[data-baseweb="select"] > div {
    background: #1E293B !important;
    border: 1.5px solid #475569 !important;
    border-radius: 10px !important;
    color: #FFFFFF !important;
}

div[data-baseweb="select"] * {
    color: #FFFFFF !important;
}

/* Premium Hero Cards */
.tutor-hero-card {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%);
    border: 1px solid rgba(99, 102, 241, 0.35);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(12px);
}

.tutor-hero-title {
    font-size: 26px;
    font-weight: 800;
    background: linear-gradient(90deg, #38BDF8 0%, #818CF8 50%, #C084FC 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}

.tutor-hero-subtitle {
    font-size: 14px;
    color: #CBD5E1;
    line-height: 1.6;
}

/* Metric Pill Cards */
.metric-card {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 16px 20px;
    text-align: left;
    transition: all 0.2s ease-in-out;
}

.metric-card:hover {
    border-color: #818CF8;
    transform: translateY(-2px);
}

.metric-val {
    font-size: 28px;
    font-weight: 700;
    color: #F8FAFC;
    margin-top: 4px;
}

.metric-lbl {
    font-size: 12px;
    font-weight: 600;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Badge Badges */
.badge-pill {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.03em;
}

.badge-easy { background: rgba(16, 185, 129, 0.2); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.4); }
.badge-medium { background: rgba(245, 158, 11, 0.2); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.4); }
.badge-hard { background: rgba(239, 68, 68, 0.2); color: #F87171; border: 1px solid rgba(239, 68, 68, 0.4); }
.badge-topic { background: rgba(99, 102, 241, 0.2); color: #A5B4FC; border: 1px solid rgba(99, 102, 241, 0.4); }
.badge-marks { background: rgba(6, 182, 212, 0.2); color: #38BDF8; border: 1px solid rgba(6, 182, 212, 0.4); }

/* Interactive Quiz Question Card */
.quiz-question-box {
    background: #1E293B;
    border: 1.5px solid #334155;
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
}

.quiz-question-text {
    font-size: 18px;
    font-weight: 600;
    line-height: 1.6;
    color: #F8FAFC;
    margin-top: 12px;
    margin-bottom: 16px;
}

/* Feedback Alert Boxes */
.feedback-correct {
    background: rgba(6, 78, 59, 0.7);
    border: 1.5px solid #10B981;
    border-radius: 12px;
    padding: 16px 20px;
    margin-top: 16px;
    color: #ECFDF5;
    font-size: 15px;
}

.feedback-incorrect {
    background: rgba(127, 29, 29, 0.7);
    border: 1.5px solid #EF4444;
    border-radius: 12px;
    padding: 16px 20px;
    margin-top: 16px;
    color: #FEF2F2;
    font-size: 15px;
}

/* Progress Bar */
div[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #38BDF8 0%, #4F46E5 100%) !important;
}

/* ========================================================= */
/* STREAMLIT ALERTS: Crystal Clear, High Contrast, Legible   */
/* ========================================================= */

[data-testid="stAlert"],
div[data-baseweb="notification"] {
    border-radius: 14px !important;
    padding: 14px 20px !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35) !important;
}

/* Ensure ALL text, paragraphs, and markdown inside alerts are bright white and sharp */
[data-testid="stAlert"] *,
[data-testid="stAlert"] p,
[data-testid="stAlert"] span,
[data-testid="stAlert"] div,
div[data-baseweb="notification"] *,
div[data-baseweb="notification"] p,
div[data-baseweb="notification"] span {
    color: #F8FAFC !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    line-height: 1.6 !important;
}

/* Info Box */
[data-testid="stAlert"]:has([data-testid="stNotificationContentInfo"]),
div[data-testid="stAlert"]:has(svg[data-testid="stIconInfo"]) {
    background: rgba(14, 116, 144, 0.35) !important;
    border: 1.5px solid #38BDF8 !important;
}

/* Warning Box */
[data-testid="stAlert"]:has([data-testid="stNotificationContentWarning"]),
div[data-testid="stAlert"]:has(svg[data-testid="stIconWarning"]) {
    background: rgba(180, 83, 9, 0.3) !important;
    border: 1.5px solid #F59E0B !important;
}

/* Success Box */
[data-testid="stAlert"]:has([data-testid="stNotificationContentSuccess"]),
div[data-testid="stAlert"]:has(svg[data-testid="stIconSuccess"]) {
    background: rgba(6, 95, 70, 0.35) !important;
    border: 1.5px solid #10B981 !important;
}

/* Error Box */
[data-testid="stAlert"]:has([data-testid="stNotificationContentError"]),
div[data-testid="stAlert"]:has(svg[data-testid="stIconError"]) {
    background: rgba(153, 27, 27, 0.35) !important;
    border: 1.5px solid #EF4444 !important;
}
</style>
"""


def apply_custom_styles():
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

