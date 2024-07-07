from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pyodbc
import time

engine = create_engine("mssql+pyodbc://localhost/fastapi?driver=ODBC+Driver+17+for+SQL+Server")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



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