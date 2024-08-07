from typing import Annotated
from fastapi import APIRouter, Request, Form, Depends, Path
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from .exceptions import RegisterException, LoginException
import sql_app.schemas as schema
from sql_app.crud import Create, Read, Update, Delete
from sql_app.database import SessionLocal
from sql_app.models import User, Product, Basket
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse, HTMLResponse
from jose import jwt
from products.router import get_current_user
from config import SECRET_KEY

router = APIRouter(prefix='/auth')

templates = Jinja2Templates(directory='./templates')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = SECRET_KEY
ALGORITHM = "HS256"


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_jwt_token(data: dict):
    from datetime import timedelta
    from datetime import datetime
    to_encode = data.copy()
    to_encode.update({'exp': datetime.utcnow() + timedelta(minutes=300)})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token) -> dict:
    decoded_token = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
    return decoded_token


@router.get('/register', response_class=HTMLResponse, include_in_schema=False)
async def get_register_form(request: Request):
    return templates.TemplateResponse(request=request, name='register.html')

@router.post('/register', response_class=HTMLResponse, include_in_schema=False)
async def get_register_info(username: Annotated[str, Form()],
                            password1: Annotated[str, Form()],
                            password2: Annotated[str, Form()],
                            db: Session = Depends(get_db)):
    if password1 != password2:
        raise RegisterException(detail='Пароли не совпадают', status_code=401)
    if len(username) < 3:
        raise RegisterException(detail='Имя слишком короткое', status_code=401)
    if len(username) > 15:
        raise RegisterException(detail='Имя слишком длинное', status_code=401)
    if len(password1) < 5:
        raise RegisterException(detail='Пароль слишком короткий', status_code=401)
    hashed_password = pwd_context.hash(password2)
    user_schema = schema.UserCreateSchema(username=username, hashed_password=hashed_password)
    Create.create_user(db, user_schema)
    return RedirectResponse(url='/auth/login', status_code=303)

@router.get('/login', include_in_schema=False)
async def get_login_form(request: Request):
    return templates.TemplateResponse(request=request, name='login.html')

@router.post('/login', include_in_schema=False)
async def get_login_form(username: Annotated[str, Form()],
                        password: Annotated[str, Form()],
                         name: Annotated[str, Form()],
                         db: Session = Depends(get_db)):
    user: schema.UserCreateSchema | None = Read.get_user_to_auth(db=db, username=username)
    if not user:
        raise LoginException(detail='Пользователь не найден', status_code=401)
    if not pwd_context.verify(password, hash=user.hashed_password):
        raise LoginException(detail='Пароль не правильный!', status_code=401)
    jwt_code = create_jwt_token(data={'username': user.username})
    response = RedirectResponse(url='/', status_code=303)
    response.set_cookie(key='token', value=jwt_code)
    return response

@router.get('/logout', response_class=RedirectResponse, include_in_schema=False)
async def logout_user():
    response = RedirectResponse(url='/', status_code=303)
    response.delete_cookie(key='token')
    return response

@router.get('/profile', include_in_schema=False)
async def get_profile_template(request: Request, current_user: User | None = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        return RedirectResponse(url='/auth/login', status_code=303)
    basket = Read.get_basket(db=db, current_user=current_user)
    full_summa = 0
    if basket:
        for elem in basket:
            full_summa += elem.full_sum
    return templates.TemplateResponse(request=request, name='profile.html', context={'user': current_user, 'basket': basket, 'full_summa': full_summa})


@router.get('/get_full_sum', status_code=200)
async def get_full_sum(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    full_sum = Read.get_full_sum(db, current_user.id)
    return {'full_sum': full_sum}

