import os
import sys
import glob
from dotenv import load_dotenv
from google import genai

# Ensure backend/ is on sys.path so sibling packages resolve correctly
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

load_dotenv(dotenv_path=os.path.join(backend_dir, ".env"))

from rag.vector_store import VectorStore


def get_embedding(client: genai.Client, text: str) -> list:
    """Embed a single piece of text using gemini-embedding-2."""
    response = client.models.embed_content(
        model="gemini-embedding-2",
        contents=text,
    )
    return response.embeddings[0].values


def split_text_by_words(text: str, chunk_size: int = 200, overlap: int = 30) -> list:
    """Split text into chunks of roughly chunk_size words with overlap."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i: i + chunk_size]
        chunks.append(" ".join(chunk_words))
        i += (chunk_size - overlap)
        if chunk_size - overlap <= 0:
            break
    return chunks


def ingest_docs():
    docs_dir = os.path.join(backend_dir, "data", "mock_docs")
    db_path = os.path.join(backend_dir, "data", "vector_store.json")

    print(f"Reading mock documents from: {docs_dir}")
    txt_files = glob.glob(os.path.join(docs_dir, "*.txt"))

    if not txt_files:
        print(f"No text files found in {docs_dir}!")
        return

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("ERROR: GEMINI_API_KEY is not set in backend/.env.")
        return

    gemini_client = genai.Client(api_key=api_key)
    store = VectorStore(db_path=db_path)

    total_chunks = 0

    for file_path in txt_files:
        filename = os.path.basename(file_path)
        print(f"\nProcessing: {filename}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        chunks = split_text_by_words(content, chunk_size=200, overlap=30)
        print(f"  Split into {len(chunks)} chunks. Embedding...")

        ids, documents, embeddings, metadatas = [], [], [], []

        for idx, chunk in enumerate(chunks):
            chunk_id = f"{filename}_chunk_{idx}"
            print(f"  [{idx + 1}/{len(chunks)}] Embedding {chunk_id} ...")
            embedding = get_embedding(gemini_client, chunk)
            ids.append(chunk_id)
            documents.append(chunk)
            embeddings.append(embedding)
            metadatas.append({"source": filename})

        store.upsert(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
        total_chunks += len(chunks)
        print(f"  Saved {len(chunks)} chunks from {filename}.")

    print(f"\nSUCCESS! Total chunks stored: {total_chunks}")
    print(f"Vector store: {db_path}")


if __name__ == "__main__":
    ingest_docs()
