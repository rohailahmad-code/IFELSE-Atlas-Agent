"""
Retriever: queries the local vector store using a Gemini embedding of the query text.
"""

import os
from dotenv import load_dotenv
from google import genai

script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
load_dotenv(dotenv_path=os.path.join(backend_dir, ".env"))

from rag.vector_store import VectorStore

_DB_PATH = os.path.join(backend_dir, "data", "vector_store.json")


def _get_store() -> VectorStore:
    return VectorStore(db_path=_DB_PATH)


def _embed_query(client: genai.Client, text: str) -> list:
    response = client.models.embed_content(
        model="gemini-embedding-2",
        contents=text,
    )
    return response.embeddings[0].values


def retrieve(query: str, n_results: int = 3) -> list[dict]:
    """
    Retrieve the top-n_results document chunks most relevant to query.

    Returns a list of dicts: {"id", "document", "metadata", "score"}
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    client = genai.Client(api_key=api_key)

    store = _get_store()
    if store.count() == 0:
        return []

    query_embedding = _embed_query(client, query)
    return store.query(query_embedding=query_embedding, n_results=n_results)
