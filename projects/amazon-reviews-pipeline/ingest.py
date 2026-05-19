from google.cloud import bigquery
import pandas as pd


df = pd.read_csv('sampled_reviews.csv')
# Clean column names (lowercase)
df.columns = df.columns.str.lower()

#---------------------------------Cast properly -----------------------------------------
df['score'] = pd.to_numeric(df['score'], errors='coerce')  # Force integer
df['time'] = pd.to_datetime(df['time'], unit='s')          # Convert Unix timestamp
df = df.dropna(subset=['score'])                           # Remove rows with bad scores
#----------------------------------------------------------------------------------------

client = bigquery.Client()
table_id = f"{client.project}.amazon_reviews_dataset.raw_reviews"

job_config = bigquery.LoadJobConfig(
    write_disposition=bigquery.WriteDisposition.WRITE_APPEND,  # WRITE_TRUNCATE to overwrite or  APPEND to append, in case of streaming more data later
    autodetect=True  # Automatically matches schema
)

job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
job.result()
print(f"✅ Uploaded {len(df)} rows")