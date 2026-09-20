import os
import shutil

from fastapi import APIRouter, File, Form, UploadFile, HTTPException

from app.db.connection import get_connection
from app.rag.ingestion import (
    extract_text_from_pdf,
    chunk_text,
    generate_embeddings,
    store_chunks,
)


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.post("/upload")
def upload_file(
    file: UploadFile = File(...),
    category: str = Form(...),
    allowed_roles: str = Form(...)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    category = category.strip()

    os.makedirs("Uploads", exist_ok=True)

    file_path = os.path.join(
        "Uploads",
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO documents (filename, category)
            VALUES (%s, %s)
            RETURNING id
            """,
            (file.filename, category)
        )

        document_id = cursor.fetchone()[0]

        roles = [
            role.strip().lower()
            for role in allowed_roles.split(",")
        ]

        for role in roles:
            cursor.execute(
                """
                INSERT INTO document_permissions
                (document_id, role)
                VALUES (%s, %s)
                """,
                (document_id, role)
            )

        conn.commit()

    finally:
        cursor.close()
        conn.close()

    text = extract_text_from_pdf(file_path)

    chunks = chunk_text(text)

    embeddings = generate_embeddings(chunks)

    store_chunks(
        chunks=chunks,
        embeddings=embeddings,
        document_id=document_id,
        filename=file.filename,
        category=category,
    )

    return {
        "message": "File uploaded successfully",
        "document_id": document_id,
        "chunks": len(chunks),
    }