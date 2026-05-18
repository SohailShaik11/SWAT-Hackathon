import os
import numpy as np
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()


def get_embedding_client() -> AzureOpenAI:
    return AzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    )


def get_embedding(text: str) -> list[float]:
    client = get_embedding_client()
    response = client.embeddings.create(
        model=os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"],
        input=text,
    )
    return response.data[0].embedding


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    a = np.array(vec_a)
    b = np.array(vec_b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def semantic_similarity(text_a: str, text_b: str) -> float:
    emb_a = get_embedding(text_a)
    emb_b = get_embedding(text_b)
    return cosine_similarity(emb_a, emb_b)
