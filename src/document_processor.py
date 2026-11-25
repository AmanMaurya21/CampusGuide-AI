
from pathlib import Path
from pypdf import PdfReader


# Location of our knowledge base
DOCUMENTS_PATH = Path("data/documents")

# Chunking settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def read_txt(file_path):
    """Read a text file."""
    return file_path.read_text(encoding="utf-8")


def read_pdf(file_path):
    """Extract text from a PDF file."""
    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def load_documents():
    """Load all supported documents."""

    documents = []

    for file_path in DOCUMENTS_PATH.iterdir():

        if file_path.suffix.lower() == ".txt":
            text = read_txt(file_path)

        elif file_path.suffix.lower() == ".pdf":
            text = read_pdf(file_path)

        else:
            continue

        if text.strip():
            documents.append({
                "source": file_path.name,
                "content": text
            })

    return documents



def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split text into chunks using paragraph and sentence boundaries."""

    import re

    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        if len(paragraph) > chunk_size:
            sentences = re.split(r"(?<=[.!?])\s+", paragraph)

            for sentence in sentences:
                if len(current_chunk) + len(sentence) > chunk_size:
                    if current_chunk.strip():
                        chunks.append(current_chunk.strip())

                    current_chunk = sentence
                else:
                    current_chunk += " " + sentence

            continue

        if len(current_chunk) + len(paragraph) > chunk_size:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())

            current_chunk = paragraph
        else:
            current_chunk += "\n\n" + paragraph if current_chunk else paragraph

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks



def process_documents():
    """Load documents and create chunks with metadata."""

    documents = load_documents()

    all_chunks = []

    for document in documents:

        chunks = chunk_text(document["content"])

        for chunk in chunks:

            if not chunk.strip():
                continue

            all_chunks.append({
                "source": document["source"],
                "content": chunk
            })

    return all_chunks


if __name__ == "__main__":

    documents = load_documents()
    chunks = process_documents()

    print(f"Documents loaded: {len(documents)}")
    print(f"Chunks created: {len(chunks)}")

    if chunks:
        print("\nSample chunk:\n")
        print(chunks[0]["content"])
