from fastapi import FastAPI, HTTPException, Response, status, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
from passlib.context import CryptContext
import pyodbc
import time
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=engine)

app = FastAPI()



server = 'localhost'
database = 'fastapi'


while True:
    try:
        conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;')
        cursor = conn.cursor()
        print("Connected to SQL Server")
        break
    except Exception as e:
        print("Error: ", e)
        time.sleep(2)

def dict_cursor(cursor):
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

my_posts = [{"title": "Post 1", "content": "Content 1", "id": 1}, 
            {"title": "yemek favouritim", "content": "Pizza seviyorum yumm", "id": 2}]


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p

def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i

@app.get("/")
def root():
    return {"message": "Gunaydin Dünya!"}


@app.get("/posts", response_model=list[schemas.Post])
def get_posts(db:Session = Depends(get_db)):
    # cursor.execute("SELECT * FROM posts")
    # posts = dict_cursor(cursor)
    posts = db.query(models.Post).all()
    return posts

@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db:Session = Depends(get_db)):
    # cursor.execute("INSERT INTO posts (title, content, published) OUTPUT INSERTED.* VALUES (?, ?, ?)",
    #                post.title, post.content, post.published)
    # new_post = dict_cursor(cursor)
    # conn.commit()
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@app.get("/posts/{id}", response_model=schemas.Post)
def get_post(id: int, db:Session = Depends(get_db)):
    # cursor.execute("SELECT * FROM posts WHERE id = ?", id)
    # post = dict_cursor(cursor)
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db:Session = Depends(get_db)):
    # cursor.execute("DELETE FROM posts WHERE id = ?", id)
    # conn.commit()
    post = db.query(models.Post).filter(models.Post.id == id)

    if post.first() == None:
        raise HTTPException(status_code=404, detail="Post id: {id} not found")
    
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}", response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db:Session = Depends(get_db)):
    # cursor.execute("UPDATE posts SET title = ?, content = ?, published = ? WHERE id = ?",
    #                 post.title, post.content, post.published, id)

    # conn.commit()
    # cursor.execute("SELECT * FROM posts WHERE id = ?", id)
    # updated_post = dict_cursor(cursor)

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post is None:
        raise HTTPException(status_code=404, detail= f"Post {id} not found")
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()


@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db:Session = Depends(get_db)):
    # Hash password
    hashed_password = pwd_context.hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user