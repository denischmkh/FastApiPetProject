import sqlalchemy
from pydantic import BaseModel


class UserReadSchema(BaseModel):
    id: int | None = None
    username: str

class UserCreateSchema(BaseModel):
    username: str
    hashed_password: str


class CreateCategorySchema(BaseModel):
    title: str

class ReadCategorySchema(CreateCategorySchema):
    id: int
    title: str

class ReadItemSchema(BaseModel):
    title: str
    description: str
    price: float
    category_id: int
    image: str
    images: str

class CreateItemSchema(ReadItemSchema):
    pass


class ReadBasketSchema(BaseModel):
    id: int
    title: str
    quantity: int
    full_sum: float