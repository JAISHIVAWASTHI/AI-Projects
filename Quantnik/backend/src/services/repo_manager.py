import pandas as pd
import chromadb
from chromadb.config import Settings
import os
from openai import OpenAI

# ----------------------------
# 1. Setup OpenAI & Chroma
# ----------------------------
# os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"
client = OpenAI()

chroma_client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet",
                                         persist_directory="./vectordb"))

collection = chroma_client.get_or_create_collection(
    name="excel_collection",
    metadata={"hnsw:space": "cosine"}  # distance metric
)

# ----------------------------
# 2. Function: Load Excel & extract metadata
# ----------------------------
def load_excel_with_metadata(file_path):
    df = pd.read_excel(file_path)
    
    metadata = {
        "file_name": os.path.basename(file_path),
        "columns": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "num_rows": len(df),
        "num_cols": len(df.columns),
    }
    return df, metadata


# ----------------------------
# 3. Convert a row into text + metadata
# ----------------------------
def prepare_records(df, file_metadata):
    records = []
    
    for idx, row in df.iterrows():
        row_text = " | ".join([f"{col}: {row[col]}" for col in df.columns])
        
        record_metadata = {
            "source_file": file_metadata["file_name"],
            "row_index": idx,
            "columns": file_metadata["columns"],
            "dtypes": file_metadata["dtypes"]
        }
        
        records.append((str(idx), row_text, record_metadata))
    
    return records


# ----------------------------
# 4. Insert into VectorDB
# ----------------------------
def embed_text(texts):
    response = client.embeddings.create(
        model="text-embedding-3-large",
        input=texts
    )
    return [d.embedding for d in response.data]


def store_records(records):
    ids = [rec[0] for rec in records]
    texts = [rec[1] for rec in records]
    metadatas = [rec[2] for rec in records]
    embeddings = embed_text(texts)
    
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas
    )


# ----------------------------
# 5. Run pipeline for all 3 Excel files
# ----------------------------
excel_files = [
    "file1.xlsx",
    "file2.xlsx",
    "file3.xlsx"
]

for f in excel_files:
    print(f"\nProcessing: {f}")
    
    df, file_meta = load_excel_with_metadata(f)
    
    records = prepare_records(df, file_meta)
    
    store_records(records)

print("\n✅ All Excel data + metadata stored in VectorDB successfully!")
