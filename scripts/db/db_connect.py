# scripts/db/db_connect.py

from sqlalchemy import create_engine

DB_USER = "postgres"
DB_PASS = ""  # default empty if no password
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "macro_dashboard"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
