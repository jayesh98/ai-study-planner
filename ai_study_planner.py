import csv
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date

TOTAL_DAILY_HOURS = 10
PROGRESS_FILE = "progress.csv"
PLAN_FILE = "tomorrow_plan.txt"


# ---------------------------
# 1. STUDY PLAN GENERATOR
# ---------------------------
def generate_study_plan():
    print("\n--- STUDY PLAN GENERATOR ---")

    exam_date = input("Enter exam date (YYYY-MM-DD): ").strip()

    try:
        exam_date = datetime.strptime(exam_date, "%Y-%m-%d")
    except ValueError:
        print("❌ Invalid date format. Please use YYYY-MM-DD.")
        return

    daily_hours = float(input("Enter daily study hours: "))

    subjects = input("Enter subjects (comma separated): ").split(",")
    weak_subjects = input("Enter weak subjects (comma separated): ").split(",")

    subjects = [s.strip() for s in subjects]
    weak_subjects = [w.strip() for w in weak_subjects]

    weak_weight = 0.6
    strong_weight = 0.4

    print("\n📘 TODAY'S STUDY PLAN")
    print("-" * 30)

    plan = {}

    for subject in subjects:
        if subject in weak_subjects:
            hours = (daily_hours * weak_weight) / len(weak_subjects)
        else:
            hours = (daily_hours * strong_weight) / (len(subjects) - len(weak_subjects))

        plan[subject] = round(hours, 2)
        print(f"{subject:<25} : {plan[subject]} hrs")

    print("-" * 30)
    print("✅ Plan generated successfully\n")

    return plan


# ---------------------------
# 2. LOG PROGRESS
# ---------------------------
def log_progress():
    print("\n--- LOG STUDY PROGRESS ---")

    subject = input("Subject name: ").strip()
    planned = float(input("Planned hours: "))
    actual = float(input("Actual studied hours: "))

    with open(PROGRESS_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([date.today(), subject, planned, actual])

    print(f"✅ Progress saved for {subject}\n")


# ---------------------------
# 3. VISUALIZE PROGRESS
# ---------------------------
def visualize_progress():
    print("\n--- VISUALIZING PROGRESS ---")

    try:
        df = pd.read_csv(
            PROGRESS_FILE,
            header=None,
            names=["Date", "Subject", "Planned", "Actual"]
        )
    except FileNotFoundError:
        print("❌ No progress data found.")
        return

    df["Planned"] = pd.to_numeric(df["Planned"], errors="coerce")
    df["Actual"] = pd.to_numeric(df["Actual"], errors="coerce")
    df = df.dropna()

    if df.empty:
        print("❌ No valid data to visualize.")
        return

    summary = df.groupby("Subject")[["Planned", "Actual"]].sum()

    summary.plot(kind="bar", figsize=(8, 5))
    plt.title("Planned vs Actual Study Hours")
    plt.ylabel("Hours")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.show()

    actual_time = df.groupby("Subject")["Actual"].sum()

    plt.figure(figsize=(6, 6))
    plt.pie(actual_time, labels=actual_time.index, autopct="%1.1f%%", startangle=140)
    plt.title("Study Time Distribution")
    plt.tight_layout()
    plt.show()


# ---------------------------
# 4. AUTO-ADJUST PLANNER
# ---------------------------
def auto_adjust_plan():
    print("\n--- AUTO-ADJUSTING TOMORROW'S PLAN ---")

    try:
        df = pd.read_csv(
            PROGRESS_FILE,
            header=None,
            names=["Date", "Subject", "Planned", "Actual"]
        )
    except FileNotFoundError:
        print("❌ No progress data found.")
        return

    df["Planned"] = pd.to_numeric(df["Planned"], errors="coerce")
    df["Actual"] = pd.to_numeric(df["Actual"], errors="coerce")
    df = df.dropna()

    if df.empty:
        print("❌ No valid progress data available.")
        return

    summary = df.groupby("Subject")[["Planned", "Actual"]].sum()
    summary["Performance"] = summary["Actual"] / summary["Planned"]

    weights = {}

    for subject, row in summary.iterrows():
        if row["Performance"] < 0.85:
            weights[subject] = 1.3
        elif row["Performance"] > 1.05:
            weights[subject] = 0.8
        else:
            weights[subject] = 1.0

    total_weight = sum(weights.values())
    plan = {
        subject: round((weight / total_weight) * TOTAL_DAILY_HOURS, 2)
        for subject, weight in weights.items()
    }

    print("\n📅 TOMORROW'S ADAPTIVE STUDY PLAN")
    print("-" * 30)

    for subject, hours in plan.items():
        print(f"{subject:<25} : {hours} hrs")

    with open(PLAN_FILE, "w") as file:
        file.write(f"AI-ADJUSTED STUDY PLAN ({date.today()})\n")
        file.write("-" * 35 + "\n")
        for subject, hours in plan.items():
            file.write(f"{subject}: {hours} hrs\n")

    print("-" * 30)
    print(f"✅ Plan saved to '{PLAN_FILE}'\n")


# ---------------------------
# MAIN MENU
# ---------------------------
def main():
    while True:
        print("\n====== AI STUDY PLANNER ======")
        print("1. Generate today's study plan")
        print("2. Log study progress")
        print("3. Visualize progress")
        print("4. Auto-adjust tomorrow's plan")
        print("5. Exit")

        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            generate_study_plan()
        elif choice == "2":
            log_progress()
        elif choice == "3":
            visualize_progress()
        elif choice == "4":
            auto_adjust_plan()
        elif choice == "5":
            print("\n👋 Thank you for using AI Study Planner. Stay consistent!\n")
            break
        else:
            print("❌ Invalid choice. Please enter 1-5.")


if __name__ == "__main__":
    main()
