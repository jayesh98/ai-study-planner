import streamlit as st
from datetime import date
import pandas as pd
import matplotlib.pyplot as plt

# ================= AUTH & DATABASE =================
from auth import create_users_table, signup_user, login_user
from database import (
    create_tables,
    save_subject,
    get_subjects,
    clear_subjects,
    save_study_log,
    get_study_logs
)

from utils import detect_low_efficiency, detect_failure_patterns

# ================= INIT =================
create_users_table()
create_tables()

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="AI Study Planner",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= SESSION =================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_email = None

if "subjects" not in st.session_state:
    st.session_state.subjects = []

if "generated_plan" not in st.session_state:
    st.session_state.generated_plan = {}

# ================= DARK UI CSS =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background: radial-gradient(circle at top, #020617, #000000);
    color: #e5e7eb;
}

.card {
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(14px);
    border-radius: 20px;
    padding: 22px;
    border: 1px solid rgba(255,255,255,0.12);
    margin-bottom: 20px;
}

.metric-box {
    background: rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 18px;
    text-align: center;
}

.subject-box {
    background: rgba(2,6,23,0.9);
    border: 1px solid #1e293b;
    border-radius: 16px;
    padding: 14px;
    margin-bottom: 12px;
}

.stButton > button {
    background: linear-gradient(135deg, #6366f1, #22d3ee);
    color: #020617;
    font-weight: 700;
    border-radius: 16px;
    border: none;
    padding: 12px 18px;
    width: 100%;
}

.remove button {
    background: linear-gradient(135deg, #ef4444, #f97316) !important;
    color: white !important;
    border-radius: 50% !important;
    width: 44px !important;
    height: 44px !important;
}
</style>
""", unsafe_allow_html=True)

# ================= LOGIN =================
if not st.session_state.authenticated:
    st.title("🔐 AI Study Planner")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if login_user(email, password):
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.session_state.subjects = get_subjects(email)
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        new_email = st.text_input("New Email")
        new_password = st.text_input("New Password", type="password")
        if st.button("Create Account"):
            if signup_user(new_email, new_password):
                st.success("Account created. Login now.")
            else:
                st.error("User already exists")

    st.stop()

# ================= SIDEBAR =================
st.sidebar.markdown(f"👤 **{st.session_state.user_email}**")
exam_date = st.sidebar.date_input("📅 Exam Date")
daily_hours = st.sidebar.number_input("⏱ Daily Study Hours", 1, 24, 6)

if st.sidebar.button("🚪 Logout"):
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.session_state.subjects = []
    st.rerun()

# ================= LOAD DATA =================
rows = get_study_logs(st.session_state.user_email)
df = pd.DataFrame(rows, columns=["Date", "Subject", "Planned", "Actual"])

if not df.empty:
    df["Date"] = pd.to_datetime(df["Date"])

# ================= TODAY SNAPSHOT (FIXED) =================
today = pd.Timestamp.today().normalize()

today_df = df[df["Date"].dt.normalize() == today] if not df.empty else pd.DataFrame()

planned_today = today_df["Planned"].sum() if not today_df.empty else 0
actual_today = today_df["Actual"].sum() if not today_df.empty else 0
consistency = round((actual_today / planned_today) * 100, 1) if planned_today else 0

st.title("📘 AI Study Planner")
st.write("🌙 Study smart. Stay consistent. Let AI guide your preparation.")

st.markdown("<div class='card'>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
c1.markdown(f"<div class='metric-box'>📘 Planned<br><b>{planned_today} hrs</b></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='metric-box'>⏱ Studied<br><b>{actual_today} hrs</b></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='metric-box'>🔥 Consistency<br><b>{consistency}%</b></div>", unsafe_allow_html=True)
st.progress(min(consistency / 100, 1.0))
st.markdown("</div>", unsafe_allow_html=True)

# ================= STUDY PLAN =================
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("🗓 Study Plan Generator")

if st.button("➕ Add Subject"):
    st.session_state.subjects.append({"name": "", "weak": False})

for i, subj in enumerate(st.session_state.subjects):
    st.markdown("<div class='subject-box'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([6, 3, 1])

    with c1:
        st.session_state.subjects[i]["name"] = st.text_input(
            f"Subject {i+1}", subj["name"], key=f"s_{i}"
        )

    with c2:
        st.session_state.subjects[i]["weak"] = st.checkbox(
            "Weak", subj["weak"], key=f"w_{i}"
        )

    with c3:
        if st.button("❌", key=f"r_{i}"):
            st.session_state.subjects.pop(i)
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

if st.button("💾 Save Subjects"):
    clear_subjects(st.session_state.user_email)
    for s in st.session_state.subjects:
        if s["name"].strip():
            save_subject(st.session_state.user_email, s["name"], s["weak"])
    st.success("Subjects saved")

if st.button("🚀 Generate Study Plan"):
    subjects = [s for s in st.session_state.subjects if s["name"].strip()]
    weak_count = sum(1 for s in subjects if s["weak"])
    total_weight = len(subjects) + weak_count

    st.session_state.generated_plan = {}

    for s in subjects:
        weight = 2 if s["weak"] else 1
        hrs = round((daily_hours * weight) / total_weight, 2)
        st.session_state.generated_plan[s["name"]] = hrs

    st.success("📘 Study plan generated")

    for k, v in st.session_state.generated_plan.items():
        st.write(f"✅ **{k}** → `{v} hrs`")

st.markdown("</div>", unsafe_allow_html=True)

# ================= LOG PROGRESS =================
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("✍️ Log Study Progress")

subjects_for_log = list(st.session_state.generated_plan.keys()) or [
    s["name"] for s in st.session_state.subjects if s["name"].strip()
]

log_subject = st.selectbox("Subject", subjects_for_log) if subjects_for_log else st.text_input("Subject")

planned = st.session_state.generated_plan.get(log_subject, 0.0)
actual = st.number_input("Actual Hours", 0.0, step=0.5)

st.info(f"Planned Hours: {planned}")

if st.button("💾 Save Progress"):
    save_study_log(
        st.session_state.user_email,
        log_subject,
        planned,
        actual
    )
    st.success("Progress saved")
    st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# ================= AI INSIGHTS =================
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("🤖 AI Insights")

if not df.empty and st.button("📊 Progress Chart"):
    summary = df.groupby("Subject")[["Planned", "Actual"]].sum()
    fig, ax = plt.subplots()
    summary.plot(kind="bar", ax=ax)
    st.pyplot(fig)

if st.button("⚙️ Efficiency Check"):
    if detect_low_efficiency(df):
        st.error("Low efficiency detected. Reduce overload or revise weak areas.")
    else:
        st.success("Efficiency healthy")

if st.button("📉 Failure Pattern"):
    patterns = detect_failure_patterns(df)
    if patterns:
        for p in patterns:
            st.error(f"Repeated underperformance in {p}")
    else:
        st.success("No failure patterns detected")

st.markdown("</div>", unsafe_allow_html=True)

# ================= EXAM STRATEGY =================
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("⏳ Exam Strategy")

confirm = st.date_input("Confirm Exam Date", key="confirm_exam")
if st.button("🎯 Show Strategy"):
    days = (pd.Timestamp(confirm) - pd.Timestamp.today()).days
    if days > 30:
        st.success("🟢 Long-term phase: Build concepts + consistency")
    elif days >= 15:
        st.warning("🟡 Mid phase: Practice + weak subject focus")
    elif days >= 0:
        st.error("🔴 Final phase: Revision + mocks only")
    else:
        st.error("Exam already passed")

st.markdown("</div>", unsafe_allow_html=True)
