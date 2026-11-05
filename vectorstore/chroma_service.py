import chromadb
import hashlib

from pathlib import Path


# DATABASE CONFIGURATION

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "chroma_data"

client = chromadb.PersistentClient(
    path=str(DB_PATH)
)

collection = client.get_or_create_collection(
    name="repomind_code_local",
    metadata={"hnsw:space": "cosine"}
)


# GENERATE STABLE CHUNK ID

def generate_chunk_id(repository, chunk):
    """
    Generate a stable ID using repository, file path
    and chunk content.
    """

    unique_text = (
        repository
        + chunk.get("file_path", "unknown")
        + str(chunk.get("start_line", 0))
        + chunk.get("content", "")
    )

    return hashlib.sha256(
        unique_text.encode("utf-8")
    ).hexdigest()


# STORE CODE CHUNKS

def store_code_chunks(chunks, embeddings, repository):

    if len(chunks) != len(embeddings):
        raise ValueError(
            "Chunks and embeddings count mismatch."
        )

    documents = []
    metadatas = []
    ids = []
    valid_embeddings = []

    seen = set()

    for chunk, embedding in zip(chunks, embeddings):

        content = chunk.get("content", "")

        if not isinstance(content, str) or not content.strip():
            continue

        # Remove duplicate content from the same file.
        unique_key = (
            chunk.get("file_path", "unknown"),
            content.strip()
        )

        if unique_key in seen:
            continue

        seen.add(unique_key)

        chunk_id = generate_chunk_id(
            repository,
            chunk
        )

        documents.append(content)

        metadatas.append({
            "repository": repository,
            "file_path": chunk.get("file_path", "unknown"),
            "name": chunk.get("name", "unknown"),
            "type": chunk.get("type", "text"),
            "start_line": int(chunk.get("start_line", 0)),
            "end_line": int(chunk.get("end_line", 0))
        })

        ids.append(chunk_id)
        valid_embeddings.append(embedding)

    if not documents:
        return 0

    # Remove previous repository data before re-indexing.
    collection.delete(
        where={"repository": repository}
    )

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=valid_embeddings,
        metadatas=metadatas
    )

    return len(documents)


# SEARCH CODE

def search_code(query_embedding, repository, n_results=5):

    if n_results < 1:
        raise ValueError(
            "n_results must be at least 1."
        )

    repository_data = collection.get(
        where={"repository": repository},
        include=["metadatas"]
    )

    repository_count = len(repository_data["ids"])

    if repository_count == 0:
        return []

    n_results = min(
        n_results,
        repository_count
    )

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where={"repository": repository},
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    matches = []

    if not results["ids"] or not results["ids"][0]:
        return []

    for index in range(len(results["ids"][0])):

        matches.append({
            "content": results["documents"][0][index],
            "metadata": results["metadatas"][0][index],
            "distance": results["distances"][0][index]
        })

    return matches


# BUILD RAG CONTEXT

def build_rag_context(search_results):

    if not search_results:
        return "No relevant code context found."

    context_parts = []

    for index, result in enumerate(
        search_results,
        start=1
    ):

        metadata = result["metadata"]

        context_parts.append(
            f"""
Context {index}

File: {metadata.get('file_path', 'unknown')}

Name: {metadata.get('name', 'unknown')}

Type: {metadata.get('type', 'unknown')}

Lines: {metadata.get('start_line', 0)}-{metadata.get('end_line', 0)}

Code:

{result['content']}
"""
        )

    return "\n".join(context_parts)