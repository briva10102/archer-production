from fastapi import FastAPI

from app.api import auth
from app.api import users
from app.api import products
from app.api import documents
from app.api import search


app = FastAPI(
    title="ARCHER",
    description="Secure enterprise AI knowledge platform",
    version="1.0.0",
)


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(documents.router)
app.include_router(search.router)