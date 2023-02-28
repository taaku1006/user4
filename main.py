import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv(".env")

USER = os.environ.get("USER")
PASSWORD = os.environ.get("PASSWORD")
HOST = os.environ.get("HOST")
DATABASE = os.environ.get("DATABASE")

# MySQL Connector/Pythonを使うためmysqlconnectorを指定する
engine=create_engine(f'mysql+mysqlconnector://{USER}:{PASSWORD}@{HOST}/{DATABASE}')

# テーブルを定義する
Base=declarative_base()
class User(Base):
    __tablename__='user'
    __table_args__=({"mysql_charset": "utf8mb4"})
    userId=Column(Integer, primary_key=True, autoincrement=True)
    name=Column(String(30), nullable=False)
    age=Column(Integer, nullable=False)


class TestUser(BaseModel):
    userId: int
    name: str 
    age: int

    class Config:
        orm_mode=True

# テーブルを作成する
Base.metadata.create_all(engine)

# セッションを作成する
Session=sessionmaker(engine)
session=Session()

app = FastAPI()

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

# データを追加する
@app.post("/users")
def post_user(user: TestUser):
    db_test_user = User(name=user.name,
                            age=user.age)
    session.add(db_test_user)
    session.commit()
    session.refresh(db_test_user)
    return db_test_user

# データを更新する
@app.put("/users/{user_id}")
def put_users(user: TestUser, user_id: int):
    target_user = session.query(User).\
        filter(User.userId == user_id).first()
    target_user.name = user.name
    target_user.age = user.age
    session.commit()
    return {target_user.name,target_user.age}

#全取得
@app.get("/users")
def user_list():
    users = session.query(User).all()
    return users

# ユーザー情報取得(id指定)
@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = session.query(User).\
        filter(User.userId == user_id).first()
    return user

#データの削除
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    session.query(User).filter(User.userId == user_id).delete()    
    session.commit()
