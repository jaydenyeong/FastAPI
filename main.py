from fastapi import FastAPI
from . import models
from .database import engine
from .routers import post, user, auth

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

server = 'localhost'
database = 'fastapi'

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Gunaydin Dünya!"}


# while True:
#     try:
#         conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;')
#         cursor = conn.cursor()
#         print("Connected to SQL Server")
#         break
#     except Exception as e:
#         print("Error: ", e)
#         time.sleep(2)