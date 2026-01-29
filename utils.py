import pandas as pd

def weekly_data(df, days=7):
    return df[df["Date"] >= (pd.Timestamp.today() - pd.Timedelta(days=days))]


def subject_performance(df):
    summary = df.groupby("Subject")[["Planned", "Actual"]].sum()
    summary["Performance"] = summary["Actual"] / summary["Planned"]
    return summary


def detect_low_efficiency(df):
    recent = weekly_data(df)
    if recent.empty:
        return None

    total_planned = recent["Planned"].sum()
    total_actual = recent["Actual"].sum()

    if total_planned == 0:
        return None

    avg_actual = total_actual / recent["Date"].nunique()
    performance = total_actual / total_planned

    if avg_actual >= 6 and performance < 0.7:
        return True
    return False


def detect_failure_patterns(df):
    recent = weekly_data(df)
    patterns = []

    for subject in recent["Subject"].unique():
        sdata = recent[recent["Subject"] == subject]
        failures = sdata[sdata["Actual"] < 0.8 * sdata["Planned"]]
        if len(failures) >= 2:
            patterns.append(subject)

    return patterns
