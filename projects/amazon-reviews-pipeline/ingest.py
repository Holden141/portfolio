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

job = client.load_table_from_dataframe(df, table_id)
job.result()
print(f"✅ Uploaded {len(df)} rows")