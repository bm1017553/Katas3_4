    import pandas as pd
    import numpy as np
    import sqlite3
    from pathlib import Path

    # -----------------------------
    # FILE PATHS
    # -----------------------------
    temp_path = r"\\Users\bmack\Documents\\Visual Studio 18N\\NASA_Exoplanet_Temp.csv"
    atm_path = r"\\Users\bmack\Documents\\Visual Studio 18\\NASA_Exoplanet_Atm_Conts.csv"
    storm_path = r"\\Users\bmack\Documents\\Visual Studio 18NASA_Exoplanet_Storm_Radius.csv"

    # -----------------------------
    # OUTPUTS
    # -----------------------------
    db_path = "nasa_exoplanets.db"
    report_path = "nasa_exoplanet_report.md"

    # -----------------------------
    # LOAD FUNCTION
    # -----------------------------
    def load_csv_safe(path, name):
        try:
            df = pd.read_csv(
                path,
                na_values=["", " ", "NA", "N/A", "null", "None"]
            )
            print(f"[LOADED] {name} | Shape: {df.shape}")
            return df
        except Exception as e:
            print(f"[ERROR] {name}: {e}")
            return None

    # -----------------------------
    # CLEAN FUNCTION
    # -----------------------------
    def clean_dataframe(df, name):
        if df is None:
            return None

        print(f"\n[CLEANING] {name}")

        # Clean column names
        df.columns = df.columns.str.strip()

        # Replace blank strings with NaN
        df.replace(r"^\s*$", np.nan, regex=True, inplace=True)

        # Convert numeric-like columns safely
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = pd.to_numeric(df[col], errors="ignore")
                if not pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = pd.to_numeric(df[col], errors="coerce")

        # Drop fully empty rows
        before = len(df)
        df.dropna(how="all", inplace=True)
        after = len(df)

        print(f"[CLEANED] Removed {before - after} empty rows")

        return df

    # -----------------------------
    # SQLITE LOADER
    # -----------------------------
    def load_to_sqlite(df, table_name, conn):
        if df is not None:
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            print(f"[SQLITE] Loaded table: {table_name} | Rows: {len(df)}")

    # -----------------------------
    # SUMMARY STATS
    # -----------------------------
    def summarize(df, name):
        if df is None:
            return f"## {name}\nNo data loaded.\n"

        summary = f"## {name}\n"
        summary += f"- Rows: {len(df)}\n"
        summary += f"- Columns: {len(df.columns)}\n\n"

        summary += "### Column Info\n"
        summary += df.dtypes.to_string() + "\n\n"

        summary += "### Missing Values\n"
        missing = df.isna().sum()
        missing = missing[missing > 0]
        summary += (missing.to_string() if len(missing) > 0 else "No missing values") + "\n\n"

        summary += "### Numeric Statistics\n"
        summary += df.describe().to_string() + "\n\n"

        return summary

    # -----------------------------
    # RUN PIPELINE
    # -----------------------------
    df_temp = clean_dataframe(load_csv_safe(temp_path, "Temperature Data"), "Temperature Data")
    df_atm = clean_dataframe(load_csv_safe(atm_path, "Atmosphere Data"), "Atmosphere Data")
    df_storm = clean_dataframe(load_csv_safe(storm_path, "Storm Radius Data"), "Storm Radius Data")

    # -----------------------------
    # SQLITE CONNECTION
    # -----------------------------
    conn = sqlite3.connect(db_path)

    load_to_sqlite(df_temp, "temperature_data", conn)
    load_to_sqlite(df_atm, "atmosphere_data", conn)
    load_to_sqlite(df_storm, "storm_radius_data", conn)

    conn.commit()
    conn.close()

    print(f"\n[SQLITE] Database saved at: {db_path}")

    # -----------------------------
    # GENERATE MARKDOWN REPORT
    # -----------------------------
    report = "# NASA Exoplanet Data Report\n\n"
    report += summarize(df_temp, "Temperature Data")
    report += summarize(df_atm, "Atmosphere Data")
    report += summarize(df_storm, "Storm Radius Data")

    Path(report_path).write_text(report, encoding="utf-8")

    print(f"[REPORT GENERATED] {report_path}")