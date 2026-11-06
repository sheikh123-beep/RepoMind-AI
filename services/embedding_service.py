from fastembed import TextEmbedding

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Load lightweight ONNX embedding model
model = TextEmbedding(
    model_name=MODEL_NAME
)


def generate_embedding(text: str):

    if not text or not text.strip():
        raise ValueError("Cannot generate embedding for empty text.")

    embedding = list(
        model.embed([text.strip()])
    )[0]

    return embedding.tolist()


def generate_embeddings(texts: list):

    valid_texts = [
        text.strip()
        for text in texts
        if isinstance(text, str) and text.strip()
    ]

    if not valid_texts:
        return []

    embeddings = model.embed(valid_texts)

    return [
        embedding.tolist()
        for embedding in embeddings
    ]