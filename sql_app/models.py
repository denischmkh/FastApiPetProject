import json

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import sqlalchemy as sql


class Base(DeclarativeBase):
    __abstract__ = True


class User(Base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(sql.Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(sql.String(length=15), unique=True)
    hashed_password: Mapped[str] = mapped_column(sql.String)

class Category(Base):
    __tablename__ = 'category'
    id: Mapped[int] = mapped_column(sql.Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(sql.String)

class Product(Base):
    __tablename__ = 'product'
    id: Mapped[int] = mapped_column(sql.Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(sql.String)
    description: Mapped[str] = mapped_column(sql.String)
    price: Mapped[float] = mapped_column(sql.Float)
    category_id: Mapped[int] = mapped_column(sql.ForeignKey('category.id'))
    image: Mapped[str] = mapped_column(sql.String)
    images: Mapped[sql.JSON] = mapped_column(sql.JSON, default=[])

class Basket(Base):
    __tablename__ = 'basket'
    id: Mapped[int] = mapped_column(sql.Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(sql.ForeignKey('product.id'))
    user_id: Mapped[int] = mapped_column(sql.ForeignKey('user.id'))
    quantity: Mapped[int] = mapped_column(sql.Integer, default=1)