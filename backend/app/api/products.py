from fastapi import APIRouter, Depends

from app.core.security import verify_token, verify_admin
from app.db.connection import get_connection
from app.schemas.requests import Product, UpdateProduct


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.delete("/{id}")
def delete_product(
    id: int,
    payload=Depends(verify_admin)
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM products
        WHERE id = %s
        """,
        (id,)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return {
        "message": "Product deleted"
    }


@router.put("/{id}")
def update_product(
    id: int,
    p: UpdateProduct,
    payload=Depends(verify_admin)
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE products
        SET name = %s,
            warranty = %s
        WHERE id = %s
        """,
        (p.name, p.warranty, id)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return {
        "message": f"Product {p.name} updated"
    }


@router.post("")
def create_product(
    p: Product,
    payload=Depends(verify_admin)
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id
        FROM users
        WHERE username = %s
        """,
        (payload["sub"],)
    )

    user = cursor.fetchone()

    cursor.execute(
        """
        INSERT INTO products(name, warranty, user_id)
        VALUES (%s, %s, %s)
        """,
        (p.name, p.warranty, user[0])
    )

    conn.commit()
    cursor.close()
    conn.close()

    return {
        "message": f"Product {p.name} added"
    }


@router.get("")
def get_products(payload=Depends(verify_token)):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id
        FROM users
        WHERE username = %s
        """,
        (payload["sub"],)
    )

    user = cursor.fetchone()

    cursor.execute(
        """
        SELECT *
        FROM products
        WHERE user_id = %s
        """,
        (user[0],)
    )

    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        "products": data
    }


@router.get("/{id}")
def get_product(id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM products WHERE id = %s",
        (id,)
    )

    data = cursor.fetchone()

    cursor.close()
    conn.close()

    return {
        "product": data
    }