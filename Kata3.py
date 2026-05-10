import requests
import pandas as pd
import time
import csv
import random
from datetime import datetime, timedelta

# -----------------------------
# CONFIG
# -----------------------------
API_KEY = "YOUR_API_KEY_HERE"  # move to env var in production
BASE_URL = "https://api.nasa.gov/DONKI/GST"
START_DATE = "2024-01-01"
END_DATE = "2024-03-01"
OUTPUT_CSV = "nasa_gst_data.csv"

CHUNK_DAYS = 10

# Retry settings
MAX_RETRIES = 5
BASE_DELAY = 1.5  # seconds

# -----------------------------
# DATE UTILITIES
# -----------------------------
def date_range_chunks(start_date, end_date, chunk_days):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    while start <= end:
        chunk_end = min(start + timedelta(days=chunk_days), end)
        yield start.strftime("%Y-%m-%d"), chunk_end.strftime("%Y-%m-%d")
        start = chunk_end + timedelta(days=1)

# -----------------------------
# API CALL WITH RETRY LOGIC
# -----------------------------
def fetch_data(start_date, end_date):
    params = {
        "startDate": start_date,
        "endDate": end_date,
        "api_key": API_KEY
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(BASE_URL, params=params, timeout=30)

            # Handle rate limiting explicitly
            if response.status_code == 429:
                wait = BASE_DELAY * attempt + random.uniform(0, 1)
                print(f"[RATE LIMIT] Attempt {attempt}/{MAX_RETRIES} → sleeping {wait:.2f}s")
                time.sleep(wait)
                continue

            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            print(f"[TIMEOUT] Attempt {attempt}/{MAX_RETRIES} for {start_date} → {end_date}")

        except requests.exceptions.ConnectionError:
            print(f"[CONNECTION ERROR] Attempt {attempt}/{MAX_RETRIES}")

        except Exception as e:
            print(f"[ERROR] Attempt {attempt}/{MAX_RETRIES}: {e}")

        # exponential backoff + jitter
        sleep_time = (BASE_DELAY ** attempt) + random.uniform(0, 1)
        print(f"[RETRYING] waiting {sleep_time:.2f}s...")
        time.sleep(sleep_time)

    print(f"[FAILED] All retries exhausted for {start_date} → {end_date}")
    return []

# -----------------------------
# FLATTEN JSON
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
# MAIN LOGIC
# -----------------------------
def main():
    all_data = []
    total_chunks = 0
    total_records = 0

    for start, end in date_range_chunks(START_DATE, END_DATE, CHUNK_DAYS):
        total_chunks += 1
        print(f"\n[INFO] Chunk {total_chunks}: {start} → {end}")

        data = fetch_data(start, end)

        if data:
            batch = [flatten_record(record) for record in data]
            all_data.extend(batch)

            total_records += len(batch)
            print(f"[OK] Retrieved {len(batch)} records (Total: {total_records})")
        else:
            print(f"[WARN] No data for {start} → {end}")

        time.sleep(1)  # polite throttling

    # -----------------------------
    # SAVE TO CSV
    # -----------------------------
    if all_data:
        df = pd.DataFrame(all_data)
        df.to_csv(OUTPUT_CSV, index=False)
        print(f"\n[SUCCESS] Saved {len(df)} records → {OUTPUT_CSV}")
    else:
        print("\n[INFO] No data collected.")

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    main()