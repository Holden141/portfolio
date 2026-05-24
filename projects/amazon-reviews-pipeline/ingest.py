from google.cloud import bigquery
import pandas as pd
from datetime import datetime

client = bigquery.Client()

def load_state():
    query = """
    SELECT last_row FROM `amazon_reviews_dataset.pipeline_state`
    WHERE pipeline_name = 'ingest'
    """
    result = client.query(query).to_dataframe()
    return result['last_row'].iloc[0] if not result.empty else 0

def save_state(last_row):
    query = f"""
    MERGE `amazon_reviews_dataset.pipeline_state` AS target
    USING (SELECT 'ingest' as pipeline_name, {last_row} as last_row, CURRENT_TIMESTAMP() as last_run) AS source
    ON target.pipeline_name = source.pipeline_name
    WHEN MATCHED THEN UPDATE SET last_row = source.last_row, last_run = source.last_run
    WHEN NOT MATCHED THEN INSERT (pipeline_name, last_row, last_run) VALUES (source.pipeline_name, source.last_row, source.last_run)
    """
    client.query(query).result()

start_row = load_state()
print(f"Starting from row {start_row}")

# Query the next 100 rows from the Reviews table in BigQuery
query = f"""
SELECT *
FROM `{client.project}.amazon_reviews_dataset.Reviews`
ORDER BY Id
LIMIT 500 OFFSET {start_row}
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