from pydoc import ModuleScanner
from typing import Optional
from fastapi import Body, FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from . import models
from .database import engine, get_db
from .models import Post
from sqlalchemy.orm import Session


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


while True:
    try:
        # Connect to your postgres DB
        conn = psycopg2.connect(
            host="localhost", database="fastapi", user="postgres", password="admin", cursor_factory=RealDictCursor
        )
        # Open a cursor to perform database operations
        cur = conn.cursor()
        print("Connected!")
        break
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        time.sleep(2)


my_posts = [
    {"title": "My first post", "content": "This is my first post", "published": True, "rating": 3, "id": 1},
    {"title": "My second post", "content": "This is my second post", "published": False, "rating": None, "id": 2},
]


def find_post(id):
    for post in posts:
        if post["id"] == id:
            return post


def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i


@app.get("/")
def root():
    return {"message": "Health Good"}


# sql alchemy
@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data": posts}


# psycopg2
# @app.get("/posts")
# def get_posts():
#     cur.execute("SELECT * FROM posts")
#     posts = cur.fetchall()
#     return {"data": posts}

# psycopg2
# @app.post("/posts", status_code=status.HTTP_201_CREATED)
# def create_posts(post: Post):
#     cur.execute(
#         "insert into posts (title, content, published) values (%s, %s, %s) returning * ",
#         (post.title, post.content, post.published),
#     )
#     new_post = cur.fetchone()
#     conn.commit()
#     return {"data": new_post}

# sqlalchemy
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post, db: Session = Depends(get_db)):
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data": new_post}


@app.get("/post/{id}")
def get_post(id: int):
    cur.execute("SELECT * FROM posts WHERE id = %s", (str(id),))
    post = cur.fetchone()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"data": post}


@app.delete("/post/{id}", status_code=status.HTTP_202_ACCEPTED)
def delete_post(id: int):
    cur.execute("DELETE FROM posts WHERE id = %s returning *", (str(id),))
    deleted_post = cur.fetchone()
    conn.commit()
    if deleted_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return Response(status_code=status.HTTP_202_ACCEPTED)


@app.put("/post/{id}", status_code=status.HTTP_205_RESET_CONTENT)
def update_post(id: int, post: Post):
    cur.execute(
        "UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s returning *",
        (
            post.title,
            post.content,
            post.published,
            str(id),
        ),
    )
    updated_post = cur.fetchone()
    conn.commit()
    if updated_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"data": updated_post}
