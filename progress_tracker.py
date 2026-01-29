import csv
from datetime import date

FILE_NAME = "progress.csv"

def log_progress():
    print("\n--- Log Study Progress ---")

    subject = input("Enter subject: ").strip()
    planned = float(input("Planned hours: "))
    actual = float(input("Actual studied hours: "))

    today = date.today()

    with open(FILE_NAME, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([today, subject, planned, actual])

    print(f"\n✅ Progress saved for {subject}\n")


if __name__ == "__main__":
    log_progress()
    input("Press Enter to exit...")
