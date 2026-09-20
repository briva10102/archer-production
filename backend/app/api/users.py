from fastapi import APIRouter, Depends

from app.core.security import verify_token
from app.db.connection import get_connection


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/profile")
def profile(payload=Depends(verify_token)):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, username
        FROM users
        WHERE username = %s
        """,
        (payload["sub"],)
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return {
        "id": user[0],
        "username": user[1]
    }