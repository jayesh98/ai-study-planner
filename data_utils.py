import pandas as pd

def load_progress_data():
    try:
        df = pd.read_csv(
            "progress.csv",
            header=None,
            names=["Date", "Subject", "Planned", "Actual"]
        )

        df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d", errors="coerce")
        df["Planned"] = pd.to_numeric(df["Planned"], errors="coerce")
        df["Actual"] = pd.to_numeric(df["Actual"], errors="coerce")

        return df.dropna()

    except FileNotFoundError:
        return pd.DataFrame()
