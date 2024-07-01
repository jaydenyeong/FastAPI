from fastapi import FastAPI, HTTPException, Response, status, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import pyodbc
import time
from sqlalchemy.orm import Session
from . import models, schemas, utils
from .database import engine, get_db
from .routers import post, user, auth

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

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Gunaydin Dünya!"}
