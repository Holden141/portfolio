from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
from google.cloud import bigquery
import pandas as pd
import os

#initialise clients
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)
bq = bigquery.Client()

# Query negative reviews
query = """
SELECT id, text, productid, score, helpfulnessnumerator, helpfulnessdenominator
FROM `amazon_reviews_dataset.stg_reviews`
WHERE rating_sentiment = 'NEGATIVE'
LIMIT 200
"""
df = bq.query(query).to_dataframe()
print(f"Got {len(df)} reviews")

if df.empty:
    print("No new negative reviews to classify.")
    exit(0)

# Identify root causes for each row
results = []
for i, row in df.iterrows():
    print(f"Processing {i+1}/{len(df)}")
    prompt = f"""Summarize the MAIN root cause of this negative review in ONE brief sentence (5-10 words).
    Review: "{row['text']}"
    Return ONLY the sentence. Nothing else.""" 
    
    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[{"role": "user", "content": prompt}]
    )
    results.append({
        "review_id": row["id"],
        "review_text": row["text"],
        "root_cause": response.choices[0].message.content.strip(),
        "score": row["score"],
        "helpfulness_numerator": row["helpfulnessnumerator"],
        "helpfulness_denominator": row["helpfulnessdenominator"]
    })

output_df = pd.DataFrame(results)


# Append to BigQuery
table_id = f"{bq.project}.amazon_reviews_dataset.reviews_with_root_causes"
job = bq.load_table_from_dataframe(output_df, table_id, job_config=bigquery.LoadJobConfig(
    write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    autodetect=True
))
job.result()
print(f"✅ Appended {len(output_df)} rows to {table_id}")