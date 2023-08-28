import sqlite3
from interface_adapters.datastore_adapters.idatastore_adapter import Datastore
from entities.chunk import Chunk

class SQL3Datastore(Datastore):
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def save_chunk(self, chunk: Chunk):
        self.cursor.execute("""
            INSERT INTO chunks (id, text, source, token_size, char_size)
            VALUES (?, ?, ?, ?, ?)
        """, (chunk.id, chunk.text, chunk.source, chunk.token_size, chunk.char_size))
        self.conn.commit()
