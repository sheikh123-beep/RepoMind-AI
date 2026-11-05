from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Load model locally
model = SentenceTransformer(MODEL_NAME, device="cpu")


def generate_embedding(text: str):
    if not text or not text.strip():
        raise ValueError("Cannot generate embedding for empty text.")

    embedding = model.encode(
        text,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    return embedding.tolist()


def generate_embeddings(texts: list):
    valid_texts = [
        text.strip()
        for text in texts
        if isinstance(text, str) and text.strip()
    ]

    if not valid_texts:
        return []

    embeddings = model.encode(
        valid_texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    return embeddings.tolist()