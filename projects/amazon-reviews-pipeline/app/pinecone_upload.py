from dotenv import load_dotenv
import os
import pandas as pd
from pinecone import Pinecone

load_dotenv()

api_key = os.getenv("PINECONE_KEY")
if not api_key:
    raise ValueError("PINECONE_KEY not found")

pc = Pinecone(api_key=api_key)

INDEX_NAME = "amazon-reviews-rag"

# Delete if exists
if INDEX_NAME in pc.list_indexes().names():
    pc.delete_index(INDEX_NAME)

# Create index with integrated embedding
pc.create_index_for_model(
    name=INDEX_NAME,
    cloud="aws",
    region="us-east-1",
    embed={
        "model": "llama-text-embed-v2",
        "field_map": {"text": "text"}
    }
)

index = pc.Index(INDEX_NAME)

# Load CSV
df = pd.read_csv('reviews_with_clusters.csv')
documents = df['original_phrase'].dropna().tolist()
clusters = df['cluster_name'].dropna().tolist()

# Prepare records - metadata must be flat
records = []
for i, (doc, cluster) in enumerate(zip(documents, clusters)):
    records.append({
        "id": str(i),
        "text": doc,
        "cluster": cluster  # 👈 Put cluster at same level as text, not inside metadata
    })

# Upsert in batches of 96
batch_size = 96
for i in range(0, len(records), batch_size):
    batch = records[i:i+batch_size]
    index.upsert_records(namespace="amazon-reviews", records=batch)
    print(f"Uploaded batch {i//batch_size + 1}/{(len(records)-1)//batch_size + 1}")

print(f"✅ Uploaded {len(records)} vectors to Pinecone")