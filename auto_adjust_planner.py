import pandas as pd
from datetime import date

TOTAL_DAILY_HOURS = 6
OUTPUT_FILE = "tomorrow_plan.txt"


def load_progress():
    df = pd.read_csv(
        "progress.csv",
        header=None,
        names=["Date", "Subject", "Planned", "Actual"]
    )

    df["Planned"] = pd.to_numeric(df["Planned"], errors="coerce")
    df["Actual"] = pd.to_numeric(df["Actual"], errors="coerce")
    df = df.dropna()

    return df


def calculate_adjusted_plan(df):
    summary = df.groupby("Subject")[["Planned", "Actual"]].sum()
    summary["Performance"] = summary["Actual"] / summary["Planned"]

    adjusted_weights = {}

    for subject, row in summary.iterrows():
        if row["Performance"] < 0.85:
            adjusted_weights[subject] = 1.3   # increase focus
        elif row["Performance"] > 1.05:
            adjusted_weights[subject] = 0.8   # reduce load
        else:
            adjusted_weights[subject] = 1.0   # keep same

    return adjusted_weights


def normalize_hours(adjusted_weights):
    total_weight = sum(adjusted_weights.values())

    final_plan = {}
    for subject, weight in adjusted_weights.items():
        final_plan[subject] = round(
            (weight / total_weight) * TOTAL_DAILY_HOURS, 2
        )

    return final_plan


def save_plan(plan):
    today = date.today()

    with open(OUTPUT_FILE, "w") as file:
        file.write(f"AI-ADJUSTED STUDY PLAN FOR {today}\n")
        file.write("-" * 35 + "\n")

        for subject, hours in plan.items():
            file.write(f"{subject}: {hours} hrs\n")

    print(f"\n✅ Tomorrow's plan saved to '{OUTPUT_FILE}'\n")


if __name__ == "__main__":
    df = load_progress()

    if df.empty:
        print("❌ No progress data found. Log progress first.")
        exit()

    adjusted_weights = calculate_adjusted_plan(df)
    tomorrow_plan = normalize_hours(adjusted_weights)

    print("\n📅 AUTO-ADJUSTED STUDY PLAN FOR TOMORROW\n")
    for subject, hours in tomorrow_plan.items():
        print(f"{subject}: {hours} hrs")

    save_plan(tomorrow_plan)
