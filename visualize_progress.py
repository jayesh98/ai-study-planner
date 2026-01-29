import pandas as pd
import matplotlib.pyplot as plt

# Load CSV safely
df = pd.read_csv(
    "progress.csv",
    header=None,
    names=["Date", "Subject", "Planned", "Actual"]
)

# Strip spaces
df["Subject"] = df["Subject"].astype(str).str.strip()

# Convert to numeric (force errors to NaN)
df["Planned"] = pd.to_numeric(df["Planned"], errors="coerce")
df["Actual"] = pd.to_numeric(df["Actual"], errors="coerce")

# Drop invalid rows
df = df.dropna(subset=["Planned", "Actual"])

# 🚨 SAFETY CHECK
if df.empty:
    print("❌ No valid numeric progress data found. Please log progress first.")
    print("\nExpected row format:")
    print("YYYY-MM-DD,Subject,PlannedHours,ActualHours")
    exit()

# -----------------------------
# BAR CHART: Planned vs Actual
# -----------------------------
summary = df.groupby("Subject")[["Planned", "Actual"]].sum()

if summary.empty:
    print("❌ Not enough data to generate charts.")
    exit()

summary.plot(kind="bar", figsize=(8, 5))
plt.title("Planned vs Actual Study Hours")
plt.ylabel("Hours")
plt.xlabel("Subject")
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()

# -----------------------------
# PIE CHART: Actual Time Split
# -----------------------------
actual_time = df.groupby("Subject")["Actual"].sum()

plt.figure(figsize=(6, 6))
plt.pie(
    actual_time,
    labels=actual_time.index,
    autopct="%1.1f%%",
    startangle=140
)
plt.title("Study Time Distribution")
plt.tight_layout()
plt.show()
