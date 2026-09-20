from app.db.connection import get_connection
from app.rag.ingestion import collection, embedding_model


def get_allowed_document_ids(role: str) -> list[int]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT document_id
        FROM document_permissions
        WHERE role = %s
        """,
        (role,)
    )

    allowed_documents = cursor.fetchall()

    cursor.close()
    conn.close()

    return [doc[0] for doc in allowed_documents]


def retrieve_documents(
    question: str,
    allowed_documents: list[int],
    n_results: int = 3
):
    if not allowed_documents:
        return []

    question_embedding = embedding_model.encode(question)

    results = collection.query(
        query_embeddings=[question_embedding.tolist()],
        n_results=n_results,
        where={
            "document_id": {
                "$in": allowed_documents
            }
        }
    )

    if not results["documents"]:
        return []

    return results["documents"][0]