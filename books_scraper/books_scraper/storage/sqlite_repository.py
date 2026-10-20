import sqlite3
from pathlib import Path

"""Data-access layer for books (keeps SQL out of the pipeline)."""
class SQLiteBookRepository:
    def __init__(self, path: str):
        self.path = path
        self.connected = None

    def connect(self):
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self.connected= sqlite3.connect(self.path)
        self.connected.execute("""CREATE TABLE IF NOT EXISTS books (
            product_url TEXT PRIMARY KEY, title TEXT, price REAL,
            availability INTEGER, image_url TEXT, category TEXT)""")
        self.connected.execute("DELETE FROM books")   
        self.connected.commit()

    def upsert(self, d: dict):
        self.connected.execute(
            "INSERT OR REPLACE INTO books VALUES (?,?,?,?,?,?)",
            (d["product_url"], d["title"], d["price"], int(d["availability"]),
             d["image_url"], d["category"]))
        self.connected.commit()

    def close(self):
        if self.connected:
            self.connected.close()