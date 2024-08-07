from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config import DB_NAME, DB_HOST, DB_PASS, DB_PORT, DB_USER

DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

engine = create_engine(url=DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)
