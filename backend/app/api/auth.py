from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException
from jose import jwt
from psycopg2.errors import UniqueViolation

from app.core.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.core.security import pwd_context
from app.db.connection import get_connection
from app.schemas.requests import Login, User


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register")
def register(user: User):
    user.username = user.username.strip().lower()

    hashed_password = pwd_context.hash(user.password)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users (username, password, role)
            VALUES (%s, %s, %s)
            """,
            (user.username, hashed_password, user.role)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "User registered successfully"}

    except UniqueViolation:
        conn.rollback()
        cursor.close()
        conn.close()

        raise HTTPException(
            status_code=400,
            detail="Username already exists."
        )


@router.post("/login")
def login(user: Login):
    user.username = user.username.strip().lower()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM users
        WHERE username = %s
        """,
        (user.username,)
    )

    db_user = cursor.fetchone()

    if db_user is None:
        cursor.close()
        conn.close()

        return {"message": "Invalid username or password"}

    if not pwd_context.verify(user.password, db_user[2]):
        cursor.close()
        conn.close()

        return {"message": "Invalid username or password"}

    payload = {
        "sub": user.username,
        "role": db_user[3],
        "exp": datetime.utcnow()
        + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    cursor.close()
    conn.close()

    return {
        "access_token": token,
        "token_type": "bearer"
    }