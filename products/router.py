import json

from fastapi import APIRouter, Request, Depends, Query, Form, File, UploadFile, Path
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sql_app.crud import Create, Read, Update, Delete
from sql_app.database import SessionLocal
from sqlalchemy.orm import Session
from sql_app.models import Category, Product, User
from typing import Annotated
import uuid


from sql_app.schemas import CreateItemSchema, CreateCategorySchema

router = APIRouter()

templates = Jinja2Templates(directory='./templates')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    from auth.router import decode_token
    token = request.cookies.get('token')
    if not token:
        return None
    try:
        token_decode = decode_token(token)
        username = token_decode.get('username')
        user = Read.get_user_to_auth(db=db, username=username)
        return user
    except:
        return None

@router.get('/', include_in_schema=False)
async def get_main_template(request: Request, db: Session = Depends(get_db), category_id: Annotated[int | None, Query()] = None, current_user: User | None = Depends(get_current_user)):
    context = {}
    categorys: list[Category] = Read.get_categorys(db=db)
    products: list[Product] = Read.get_products(db=db, category_id=category_id)
    context.update({'categorys': categorys, 'products': products, 'user': current_user})
    return templates.TemplateResponse(request=request, name='index.html', context=context)

@router.post('/add_product')
async def get_new_product_data(title: Annotated[str, Form(description='Название товара')],
                               description: Annotated[str, Form(description='Описание товара')],
                               price: Annotated[float, Form(description='Цена товара')],
                               image: Annotated[UploadFile, File(description='Фото для карточки с товаром')],
                               images: Annotated[list[UploadFile], File(description='Дополнительные фото товара')],
                               category_id: Annotated[int, Form(description='Айди категории к которой относится товар')],
                               db: Session = Depends(get_db)):
    photo_name = str(uuid.uuid4()) + '.png'
    with open(f'./styles/img/{photo_name}', 'wb') as photo:
        photo.write(image.file.read())
    images_optional = []
    for image in images:
        photo_name = str(uuid.uuid4()) + '.png'
        with open(f'./styles/img/{photo_name}', 'wb') as photo:
            photo.write(image.file.read())
            images_optional.append(photo_name)
    product = CreateItemSchema(title=title, description=description, price=price, image=photo_name, images=json.dumps(images_optional), category_id=category_id)
    Create.create_item(db=db, item_schema=product)

@router.post('/add_category')
async def get_new_category_data(title: Annotated[str, Form()], db: Session = Depends(get_db)):
    category_schema = CreateCategorySchema(title=title)
    Create.create_category(db=db, category_schema=category_schema)

@router.post('/add_to_basket/{product_id}', include_in_schema=False, status_code=200)
async def add_in_basket(request: Request, product_id: int, current_user: User | None = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        return RedirectResponse(url='/auth/login', status_code=303)
    Update.add_item_to_backet(db=db, product_id=product_id, current_user=current_user)


@router.post('/delete_item/{basket_id}', include_in_schema=False)
async def delete_item_from_basket(basket_id: Annotated[int, Path()], request: Request, db: Session = Depends(get_db)):
    Delete.delete_item_from_backet(db=db, basket_position_id=basket_id)
    referer_url = request.headers.get('referer')
    return RedirectResponse(url=referer_url, status_code=303)