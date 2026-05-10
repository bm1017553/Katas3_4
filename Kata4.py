import pandas as pd

# -----------------------------
# FILE PATHS (update if needed)
# -----------------------------
temp_path = r"\\Users\bmack\Documents\\Visual Studio 18N\\NASA_Exoplanet_Temp.csv"
atm_path = r"\\Users\bmack\Documents\\Visual Studio 18\\NASA_Exoplanet_Atm_Conts.csv"
storm_path = r"\\Users\bmack\Documents\\Visual Studio 18NASA_Exoplanet_Storm_Radius.csv"

# -----------------------------
# READ CSV FILES
# -----------------------------
try:
    df_temp = pd.read_csv(temp_path)
    print(f"Loaded: {temp_path} | Shape: {df_temp.shape}")

    df_atm = pd.read_csv(atm_path)
    print(f"Loaded: {atm_path} | Shape: {df_atm.shape}")

    df_storm = pd.read_csv(storm_path)
    print(f"Loaded: {storm_path} | Shape: {df_storm.shape}")

except FileNotFoundError as e:
    print(f"File not found: {e.filename}")
except Exception as e:
    print(f"Error reading CSV files: {e}")

# -----------------------------
# OPTIONAL: QUICK INSPECTION
# -----------------------------
print("\nTemp Data Preview:")
print(df_temp.head())

print("\nAtmosphere Data Preview:")
print(df_atm.head())

print("\nStorm Radius Data Preview:")
print(df_storm.head())