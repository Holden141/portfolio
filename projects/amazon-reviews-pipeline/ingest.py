from google.cloud import bigquery
import pandas as pd
import os
import json
from datetime import datetime


#----State file---------------------
STATE_FILE = "state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f).get("last_row", 0)
    return 0

def save_state(last_row):
    with open(STATE_FILE, 'w') as f:
        json.dump({"last_row": last_row, "last_run": datetime.now().isoformat()}, f, indent=2)

# Initialize BigQuery client
client = bigquery.Client()
start_row = load_state()
print(f"Starting from row {start_row}")

# Query the next 100 rows from the Reviews table in BigQuery
query = f"""
SELECT *
FROM `{client.project}.amazon_reviews_dataset.Reviews`
ORDER BY Id
LIMIT 100 OFFSET {start_row}
"""
df = client.query(query).to_dataframe()

if len(df) == 0:
    print("No new rows.")
    exit(0)



#---------------------------------Cast properly -----------------------------------------
df.columns = df.columns.str.lower()
df['score'] = pd.to_numeric(df['score'], errors='coerce')  # Force integer
df['time'] = pd.to_datetime(df['time'], unit='s')          # Convert Unix timestamp
df = df.dropna(subset=['score'])                           # Remove rows with bad scores
#----------------------------------------------------------------------------------------

#------------Upload---------------
table_id = f"{client.project}.amazon_reviews_dataset.raw_reviews"

job_config = bigquery.LoadJobConfig(
    write_disposition=bigquery.WriteDisposition.WRITE_APPEND,  # WRITE_TRUNCATE to overwrite or APPEND
    autodetect=True  # Automatically matches schema
)

job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
job.result()
#------------------------------------------------------------------------
# Update State
new_position = start_row + len(df)
save_state(new_position)
print(f"✅ Uploaded {len(df)} rows. Next start: {new_position}")