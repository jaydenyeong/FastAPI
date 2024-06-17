from fastapi import FastAPI, HTTPException, Response, status
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import pyodbc
import time

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True

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

@app.get("/posts")
def get_posts():
    cursor.execute("SELECT * FROM posts")
    posts = dict_cursor(cursor)
    # posts = cursor.fetchall()
    return {"data": posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    cursor.execute("INSERT INTO posts (title, content, published) OUTPUT INSERTED.* VALUES (?, ?, ?)",
                   post.title, post.content, post.published)
    new_post = dict_cursor(cursor)
    conn.commit()
    return {"data": new_post}

@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    cursor.execute("SELECT * FROM posts WHERE id = ?", id)
    post = dict_cursor(cursor)
    if not post:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Post not found!"}
    return {"post_detail": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    # delete post
    index = find_index_post(id)

    if index is None:
        raise HTTPException(status_code=404, detail= f"Post {id} not found")

    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    index = find_index_post(id)
    if index is None:
        raise HTTPException(status_code=404, detail= f"Post {id} not found")
    post_dict = post.dict()
    post_dict['id'] = id
    my_posts[index] = post_dict
    return {"data": post_dict}