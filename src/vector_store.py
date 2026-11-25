
import pickle
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer

from src.document_processor import process_documents


# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
VECTOR_STORE_PATH = BASE_DIR / "vector_store"

INDEX_PATH = VECTOR_STORE_PATH / "campusguide.index"
METADATA_PATH = VECTOR_STORE_PATH / "metadata.pkl"

# Embedding model
MODEL_NAME = "all-MiniLM-L6-v2"


def build_vector_store():
    """Create embeddings and save the FAISS index."""

    print("Loading documents and chunks...")
    chunks = process_documents()

    if not chunks:
        print("No chunks found.")
        return

    print(f"Chunks loaded: {len(chunks)}")

    print("Loading embedding model...")
    model = SentenceTransformer(MODEL_NAME)

    texts = [chunk["content"] for chunk in chunks]

    print("Generating embeddings...")
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        convert_to_numpy=True
    )

    # FAISS requires float32 vectors
    embeddings = embeddings.astype("float32")

    print("Creating FAISS index...")
    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Save index
    VECTOR_STORE_PATH.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_PATH))

    # Save chunk metadata
    with open(METADATA_PATH, "wb") as file:
        pickle.dump(chunks, file)

    print("\nVector store created successfully!")
    print(f"Total vectors: {index.ntotal}")
    print(f"Vector dimensions: {dimension}")
    print(f"Index saved at: {INDEX_PATH}")


def load_vector_store():
    """Load the saved FAISS index and metadata."""

    if not INDEX_PATH.exists() or not METADATA_PATH.exists():
        raise FileNotFoundError(
            "Vector store not found. Build it first."
        )

    index = faiss.read_index(str(INDEX_PATH))

    with open(METADATA_PATH, "rb") as file:
        metadata = pickle.load(file)

    model = SentenceTransformer(MODEL_NAME)

    return index, metadata, model



def search_documents(query, top_k=3, distance_threshold=1.3):
    """Retrieve relevant chunks and filter weak matches."""

    index, metadata, model = load_vector_store()

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True
    ).astype("float32")

    top_k = min(top_k, index.ntotal)

    distances, indices = index.search(query_embedding, top_k)

    results = []

    for rank, idx in enumerate(indices[0]):
        if idx == -1:
            continue

        distance = float(distances[0][rank])

        # Filter weak matches
        if distance > distance_threshold:
            continue

        results.append({
            "rank": len(results) + 1,
            "distance": distance,
            "source": metadata[idx]["source"],
            "content": metadata[idx]["content"]
        })

    return results



if __name__ == "__main__":
    build_vector_store()
