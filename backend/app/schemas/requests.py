from pydantic import BaseModel


class Product(BaseModel):
    name: str
    warranty: int


class User(BaseModel):
    username: str
    password: str
    role: str


class Login(BaseModel):
    username: str
    password: str


class Question(BaseModel):
    question: str


class UpdateProduct(BaseModel):
    name: str
    warranty: int


class SearchRequest(BaseModel):
    question: str