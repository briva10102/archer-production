from fastapi import APIRouter, Depends

from app.core.security import verify_token
from app.rag.retrieval import get_allowed_document_ids, retrieve_documents
from app.services.conversation import get_history, add_exchange
from app.services.llm import generate_answer
from app.schemas.requests import SearchRequest


router = APIRouter(
    prefix="/search",
    tags=["Search"]
)


@router.post("")
def search(
    request: SearchRequest,
    payload=Depends(verify_token)
):
    role = payload["role"]

    allowed_documents = get_allowed_document_ids(role)

    if not allowed_documents:
        return {
            "answer": "I couldn't find any information you're authorized to access.",
            "sources": []
        }

    documents = retrieve_documents(
        question=request.question,
        allowed_documents=allowed_documents,
        n_results=3,
    )

    if not documents:
        return {
            "answer": "I couldn't find that information in the uploaded document.",
            "sources": []
        }

    context = "\n\n".join(documents)

    history = get_history()

    answer = generate_answer(
        question=request.question,
        context=context,
        history=history,
    )

    add_exchange(
        question=request.question,
        answer=answer,
    )

    return {
        "answer": answer,
        "sources": documents,
    }