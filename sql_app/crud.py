import sqlalchemy as sql
from sqlalchemy.orm import Session
from .schemas import UserReadSchema, UserCreateSchema, CreateCategorySchema, ReadBasketSchema, ReadCategorySchema, \
    ReadItemSchema, CreateItemSchema
from .models import User, Category, Product, Basket


class Create:
    @staticmethod
    def create_category(db: Session, category_schema: CreateCategorySchema):
        db.execute(sql.insert(Category).values(**category_schema.dict()))
        db.commit()

    @staticmethod
    def create_item(db: Session, item_schema: CreateItemSchema):
        db.execute(sql.insert(Product).values(**item_schema.dict()))
        db.commit()

    @staticmethod
    def create_user(db: Session, user_create_schema: UserCreateSchema):
        db.execute(sql.insert(User).values(**user_create_schema.dict()))
        db.commit()


class Read:
    @staticmethod
    def get_user_to_auth(db: Session, username: str) -> User | None:
        result = db.execute(sql.select(User).where(User.username == username))
        user_from_db = result.scalars().first()
        if not user_from_db:
            return None
        return user_from_db



    @staticmethod
    def get_categorys(db: Session):
        result = db.execute(sql.select(Category))
        return result.scalars().all()

    @staticmethod
    def get_products(db: Session, category_id: int | None):
        if not category_id:
            result = db.execute(sql.select(Product))
        else:
            result = db.execute(sql.select(Product).where(Product.category_id == category_id))
        return result.scalars().all()

    @staticmethod
    def get_basket(db: Session, current_user: User) -> list[ReadBasketSchema] | None:
        request = db.execute(sql.select(Basket).where(Basket.user_id == current_user.id))
        result = request.scalars().all()
        if not result:
            return None
        products = []
        for elem in result:
            request = db.execute(sql.select(Product).where(Product.id == elem.product_id))
            result = request.scalars().first()
            product_in_basket = ReadBasketSchema(id=elem.id, title=result.title, quantity=elem.quantity,
                                                 full_sum=result.price * elem.quantity)
            products.append(product_in_basket)
        return products

    @staticmethod
    def get_full_sum(db: Session, user_id: int):
        result = db.execute(sql.select(Basket).where(Basket.user_id == user_id))
        full_basket = result.scalars().all()
        full_sum = 0
        for elem in full_basket:
            result = db.execute(sql.select(Product).where(Product.id == elem.product_id))
            product = result.scalars().first()
            full_sum += (product.price * elem.quantity)
        return full_sum


class Update:
    @staticmethod
    def add_item_to_backet(db: Session, product_id: int, current_user: User):
        check_in_backet = db.execute(
            sql.select(Basket).where(Basket.product_id == product_id, Basket.user_id == current_user.id))
        result = check_in_backet.scalars().first()
        if not result:
            db.execute(sql.insert(Basket).values(product_id=product_id, user_id=current_user.id))
            db.commit()
            return
        db.execute(sql.update(Basket).where(Basket.product_id == product_id, Basket.user_id == current_user.id).values(
            quantity=result.quantity + 1))
        db.commit()
        return


class Delete:
    @staticmethod
    def delete_item_from_backet(db: Session, basket_position_id: int):
        db.execute(sql.delete(Basket).where(Basket.id == basket_position_id))
        db.commit()
