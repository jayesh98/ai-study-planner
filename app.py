import streamlit as st
import csv
from datetime import date
import matplotlib.pyplot as plt
import pandas as pd

from data_utils import load_progress_data
from utils import weekly_data, subject_performance, detect_low_efficiency, detect_failure_patterns

# ------------------ UI HEADER ------------------
st.title("📘 AI Study Planner")
st.write("Personalized study planning using Python")

# ------------------ STUDY PLAN GENERATOR ------------------
st.header("🗓 Study Plan Generator")

exam_date = st.date_input("Exam Date")
daily_hours = st.number_input("Daily Study Hours", min_value=1, max_value=24, value=6)
subjects = st.text_input("Subjects (comma separated)")
weak_subjects = st.text_input("Weak Subjects (comma separated)")

if st.button("Generate Study Plan"):
    subject_list = [s.strip() for s in subjects.split(",") if s.strip()]
    weak_list = [w.strip() for w in weak_subjects.split(",") if w.strip()]

    if not subject_list or not weak_list:
        st.error("Please enter both subjects and weak subjects.")
    else:
        st.subheader("📘 Today's Study Plan")
        for subject in subject_list:
            if subject in weak_list:
                hrs = (daily_hours * 0.6) / len(weak_list)
            else:
                hrs = (daily_hours * 0.4) / (len(subject_list) - len(weak_list))
            st.write(f"**{subject}** : {round(hrs,2)} hrs")

# ------------------ LOG PROGRESS ------------------
st.header("✍️ Log Study Progress")

log_subject = st.text_input("Subject")
planned = st.number_input("Planned Hours", 0.0, step=0.5)
actual = st.number_input("Actual Hours", 0.0, step=0.5)

if st.button("Save Progress"):
    with open("progress.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([date.today(), log_subject, planned, actual])
    st.success("Progress saved!")

# ------------------ CHARTS ------------------
st.header("📊 Progress Charts")

if st.button("Show Charts"):
    df = load_progress_data()
    if df.empty:
        st.warning("No data available.")
    else:
        summary = df.groupby("Subject")[["Planned", "Actual"]].sum()
        fig, ax = plt.subplots()
        summary.plot(kind="bar", ax=ax)
        st.pyplot(fig)

# ------------------ WEEKLY SUMMARY ------------------
st.header("📅 Weekly Performance Summary")

if st.button("Show Weekly Summary"):
    df = load_progress_data()
    recent = weekly_data(df)

    if recent.empty:
        st.warning("No recent data.")
    else:
        total_p = recent["Planned"].sum()
        total_a = recent["Actual"].sum()
        consistency = round((total_a / total_p) * 100, 2)

        perf = subject_performance(recent)
        st.write(f"Consistency: **{consistency}%**")
        st.write(f"Best Subject: **{perf['Performance'].idxmax()}**")
        st.write(f"Weak Subject: **{perf['Performance'].idxmin()}**")

# ------------------ LOW EFFICIENCY ------------------
st.header("⚙️ Study Efficiency Check")

if st.button("Check Efficiency"):
    df = load_progress_data()
    if detect_low_efficiency(df):
        st.error("Low efficiency detected. Reduce load & take breaks.")
    else:
        st.success("Efficiency looks healthy!")

# ------------------ FAILURE PATTERN ------------------
st.header("📉 Failure Pattern Detector")

if st.button("Detect Patterns"):
    df = load_progress_data()
    patterns = detect_failure_patterns(df)

    if patterns:
        for s in patterns:
            st.error(f"Repeated difficulty in **{s}**")
    else:
        st.success("No failure patterns detected.")

# ------------------ EXAM STRATEGY ------------------
st.header("⏳ Exam Strategy")

exam_confirm = st.date_input("Confirm Exam Date")

if st.button("Show Strategy"):
    days_left = (pd.Timestamp(exam_confirm) - pd.Timestamp.today()).days

    if days_left > 30:
        st.success("Long-term phase: Build fundamentals.")
    elif 15 <= days_left <= 30:
        st.warning("Mid-phase: Focus on weak areas + revision.")
    else:
        st.error("Final phase: Revision & mock tests only.")
