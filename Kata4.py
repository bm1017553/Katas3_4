import pandas as pd
import numpy as np

# -----------------------------
# FILE PATHS
# -----------------------------
temp_path = r"\\Users\bmack\Documents\\Visual Studio 18N\\NASA_Exoplanet_Temp.csv"
atm_path = r"\\Users\bmack\Documents\\Visual Studio 18\\NASA_Exoplanet_Atm_Conts.csv"
storm_path = r"\\Users\bmack\Documents\\Visual Studio 18NASA_Exoplanet_Storm_Radius.csv"

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def load_csv_safe(path, name):
    """Safely load CSV with basic error handling."""
    try:
        df = pd.read_csv(
            path,
            na_values=["", " ", "NA", "N/A", "null", "None"]
        )
        print(f"[LOADED] {name} | Shape: {df.shape}")
        return df
    except FileNotFoundError:
        print(f"[ERROR] File not found: {path}")
    except Exception as e:
        print(f"[ERROR] Reading {name}: {e}")
    return None


def clean_dataframe(df, name):
    """Clean missing values + fix datatype issues."""

    if df is None:
        return None

    print(f"\n[CLEANING] {name}")

    # -----------------------------
    # STEP 1: Strip column names
    # -----------------------------
    df.columns = df.columns.str.strip()

    # -----------------------------
    # STEP 2: Replace blank strings
    # -----------------------------
    df.replace(r"^\s*$", np.nan, regex=True, inplace=True)

    # -----------------------------
    # STEP 3: Convert numeric columns safely
    # -----------------------------
    for col in df.columns:
        # Try converting object columns to numeric if possible
        if df[col].dtype == "object":
            converted = pd.to_numeric(df[col], errors="ignore")

            # If conversion succeeded for majority of values
            if pd.api.types.is_numeric_dtype(converted):
                df[col] = converted
            else:
                # Force numeric conversion where possible
                df[col] = pd.to_numeric(df[col], errors="coerce")

    # -----------------------------
    # STEP 4: Missing value report
    # -----------------------------
    missing = df.isna().sum()
    print(f"[MISSING VALUES - {name}]")
    print(missing[missing > 0] if missing.sum() > 0 else "No missing values")

    # -----------------------------
    # STEP 5: Drop fully empty rows
    # -----------------------------
    before = len(df)
    df.dropna(how="all", inplace=True)
    after = len(df)

    print(f"[CLEANED ROWS] Removed {before - after} empty rows")

    return df


def preview(df, name):
    """Safe preview function."""
    if df is not None:
        print(f"\n--- {name} Preview ---")
        print(df.head())


# -----------------------------
# PIPELINE EXECUTION
# -----------------------------
df_temp = load_csv_safe(temp_path, "Temperature Data")
df_atm = load_csv_safe(atm_path, "Atmosphere Data")
df_storm = load_csv_safe(storm_path, "Storm Radius Data")

df_temp = clean_dataframe(df_temp, "Temperature Data")
df_atm = clean_dataframe(df_atm, "Atmosphere Data")
df_storm = clean_dataframe(df_storm, "Storm Radius Data")

# -----------------------------
# OPTIONAL PREVIEW
# -----------------------------
preview(df_temp, "Temperature Data")
preview(df_atm, "Atmosphere Data")
preview(df_storm, "Storm Radius Data")