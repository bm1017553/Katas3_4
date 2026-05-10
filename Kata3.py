import requests
import pandas as pd
import time
from datetime import datetime, timedelta

# -----------------------------
# CONFIG
# -----------------------------
API_KEY = "YOUR_API_KEY_HERE"
BASE_URL = "https://api.nasa.gov/DONKI/GST"
START_DATE = "2024-01-01"
END_DATE = "2024-03-01"
OUTPUT_CSV = "nasa_gst_data.csv"

CHUNK_DAYS = 10

# -----------------------------
# TEST RETRY SETTINGS
# -----------------------------
MAX_RETRIES = 4
FIXED_DELAY = 2  # seconds (constant for testing)

# If True → stops immediately on first failure (debug mode)
FAIL_FAST = False

# -----------------------------
# DATE CHUNKS
# -----------------------------
def date_range_chunks(start_date, end_date, chunk_days):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    while start <= end:
        chunk_end = min(start + timedelta(days=chunk_days), end)
        yield start.strftime("%Y-%m-%d"), chunk_end.strftime("%Y-%m-%d")
        start = chunk_end + timedelta(days=1)

# -----------------------------
# API CALL (TEST RETRY LOGIC)
# -----------------------------
def fetch_data(start_date, end_date):
    params = {
        "startDate": start_date,
        "endDate": end_date,
        "api_key": API_KEY
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"[TRY] Attempt {attempt}/{MAX_RETRIES} → {start_date} to {end_date}")

            response = requests.get(BASE_URL, params=params, timeout=30)

            # Simulate visible rate-limit handling
            if response.status_code == 429:
                print(f"[RATE LIMIT] Attempt {attempt} hit 429")
                raise Exception("Rate limited")

            response.raise_for_status()
            print(f"[SUCCESS] Chunk succeeded on attempt {attempt}")
            return response.json()

        except Exception as e:
            print(f"[FAIL] Attempt {attempt}: {e}")

            if FAIL_FAST:
                print("[DEBUG MODE] FAIL_FAST enabled → stopping immediately")
                return []

            if attempt < MAX_RETRIES:
                print(f"[WAIT] Sleeping {FIXED_DELAY}s before retry...")
                time.sleep(FIXED_DELAY)
            else:
                print(f"[GIVE UP] Exhausted retries for {start_date} → {end_date}")

    return []

# -----------------------------
# FLATTEN
# -----------------------------
def flatten_record(record):
    return {
        "gst_id": record.get("gstID"),
        "start_time": record.get("startTime"),
        "all_kp_index": str(record.get("allKpIndex")),
        "link": record.get("link"),
        "linked_events_count": len(record.get("linkedEvents", []))
    }

# -----------------------------
# MAIN
# -----------------------------
def main():
    all_data = []
    total_chunks = 0

    for start, end in date_range_chunks(START_DATE, END_DATE, CHUNK_DAYS):
        total_chunks += 1
        print(f"\n[CHUNK {total_chunks}] {start} → {end}")

        data = fetch_data(start, end)

        if data:
            for record in data:
                all_data.append(flatten_record(record))
            print(f"[INFO] Added {len(data)} records")
        else:
            print("[WARN] No data returned for chunk")

        time.sleep(1)

    # -----------------------------
    # SAVE
    # -----------------------------
    if all_data:
        df = pd.DataFrame(all_data)
        df.to_csv(OUTPUT_CSV, index=False)
        print(f"\n[SAVED] {len(df)} rows → {OUTPUT_CSV}")
    else:
        print("\n[INFO] No data collected.")

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    main()