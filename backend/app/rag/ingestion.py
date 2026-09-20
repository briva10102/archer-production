from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb


embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

chroma_client = chromadb.PersistentClient(path="chroma_db")

collection = chroma_client.get_or_create_collection(
    name="solar_manuals"
)


def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text

    return text


def chunk_text(text: str, chunk_size: int = 500) -> list[str]:
    chunks = []

    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])

    return chunks


def generate_embeddings(chunks: list[str]):
    embeddings = []

    for chunk in chunks:
        embeddings.append(
            embedding_model.encode(chunk)
        )

    return embeddings


def store_chunks(
    chunks: list[str],
    embeddings,
    document_id: int,
    filename: str,
    category: str
):
    for i in range(len(chunks)):
        collection.add(
            ids=[f"{filename}_{i}"],
            documents=[chunks[i]],
            embeddings=[embeddings[i].tolist()],
            metadatas=[
                {
                    "document_id": document_id,
                    "source": filename,
                    "category": category
                }
            ]
        )