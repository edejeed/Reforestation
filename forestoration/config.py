from os import getenv
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = getenv("SECRET_KEY")
    MYSQL_DATABASE_HOST = getenv("MYSQL_DATABASE_HOST")
    MYSQL_DATABASE_USER = getenv("MYSQL_DATABASE_USER")
    MYSQL_DATABASE_PASSWORD = getenv("MYSQL_DATABASE_PASSWORD")
    MYSQL_DATABASE_DB = getenv("MYSQL_DATABASE_DB")