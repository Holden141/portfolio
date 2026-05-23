import os
from dotenv import load_dotenv
from openai import OpenAI
from google.cloud import bigquery
import pandas as pd

from sentence_transformers import SentenceTransformer
import umap
import hdbscan

load_dotenv()

#initialise clients
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)
bq = bigquery.Client()

# Query negative reviews
query = """
SELECT id, text, productid, score
FROM `amazon_reviews_dataset.stg_reviews`
WHERE rating_sentiment = 'NEGATIVE'
LIMIT 200
"""
df = bq.query(query).to_dataframe()
print(f"Got {len(df)} reviews")

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
        "root_cause": response.choices[0].message.content.strip()
    })

# Save to CSV
output_df = pd.DataFrame(results)
print("Root Causes Identified")

phrases = output_df["root_cause"].astype(str).tolist()

#-----------------------Generate EMBEDDINGS----------------------------------------
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2") 
embeddings = model.encode(phrases, show_progress_bar=True)
print(f"Embeddings shape: {embeddings.shape}")

#----------------------Clustering-----------------------------------------------
umap_reducer = umap.UMAP(n_components=5, random_state=42, n_neighbors=15, min_dist=0.0)
embeddings_umap = umap_reducer.fit_transform(embeddings)
print(f"UMAP reduced shape: {embeddings_umap.shape}")

# Step 4: Cluster with HDBSCAN
clusterer = hdbscan.HDBSCAN(min_cluster_size=3, min_samples=1, metric='euclidean')
cluster_labels = clusterer.fit_predict(embeddings_umap)
print(f"Found {len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)} clusters")
print(f"Cluster distribution:\n{pd.Series(cluster_labels).value_counts().sort_index()}")

# Create df_clusters from the clustering results
df_clusters = pd.DataFrame({
    'original_phrase': phrases,
    'cluster_id': cluster_labels
})
#-----------------------Build Summary---------------------------
cluster_summary = "\n".join([
    f"Cluster {cid}: {df_clusters[df_clusters['cluster_id'] == cid]['original_phrase'].head(3).tolist()}"
    for cid in sorted(df_clusters['cluster_id'].unique()) if cid != -1
])

# Get names from LLM
prompt = f"""Return a Python dict mapping cluster_id to a SHORT category name (2-4 words MAXIMUM).

Examples of good names:
- "Misleading Label"
- "Texture Issues" 
- "Packaging Damage"
- "Taste Problems"

Do NOT use full sentences. Do NOT use all caps. Keep it short.

Here are the clusters:
{cluster_summary}

Format: {{0: "Short Name", 22: "Short Name", ...}}"""
response = client.chat.completions.create(model="deepseek-v4-flash", messages=[{"role": "user", "content": prompt}], temperature=0.3)

# Parse and map
cluster_names = eval(response.choices[0].message.content.strip())
cluster_names = {int(k): v for k, v in cluster_names.items()}
cluster_names[-1] = "Other"
df_clusters['cluster_name'] = df_clusters['cluster_id'].map(cluster_names)

output_df['cluster_id'] = df_clusters['cluster_id']
output_df['cluster_name'] = df_clusters['cluster_name']

#---------- Save to csv.
output_df.to_csv("reviews_with_clusters.csv", index=False)
print('reviews_with_clusters.csv Written.')