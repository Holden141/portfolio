import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.ensemble import IsolationForest
from google.cloud import bigquery

bq = bigquery.Client()

# Load reviews with root causes
query = """
SELECT review_text, root_cause, score, helpfulness_numerator, helpfulness_denominator
FROM `amazon_reviews_dataset.reviews_with_root_causes`
"""
df = bq.query(query).to_dataframe()

if len(df) < 20:
    print("Not enough data for anomaly detection")
    exit(0)

# Generate embeddings from root cause text
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(df['root_cause'].tolist())

# Add helpfulness ratio as a feature
df['helpfulness_ratio'] = df['helpfulness_numerator'] / df['helpfulness_denominator'].replace(0, 1)

# Build feature matrix
features = np.hstack([
    embeddings,
    df[['score', 'helpfulness_ratio']].values
])

# Train Isolation Forest
iso_forest = IsolationForest(contamination=0.1, random_state=42)
df['is_anomaly'] = iso_forest.fit_predict(features) == -1

# Write results to BigQuery
table_id = f"{bq.project}.amazon_reviews_dataset.anomalous_reviews"
job = bq.load_table_from_dataframe(
    df[df['is_anomaly']],
    table_id,
    job_config=bigquery.LoadJobConfig(write_disposition='WRITE_TRUNCATE')
)
job.result()
print(f"Found {df['is_anomaly'].sum()} anomalous reviews")