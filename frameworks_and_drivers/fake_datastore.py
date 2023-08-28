from interface_adapters.datastore_adapters.idatastore_adapter import Datastore
from entities.chunk import Chunk

class FakeDatastore(Datastore):
    def __init__(self, db_name):
        print("FakeDatastore.__init__")

    def save_chunk(self, chunk: Chunk):
        print(f"Chunk saved to fake datastore id:{chunk.id} text: {chunk.text[:20]} source: {chunk.source} token_size: {chunk.token_size} char_size: {chunk.char_size}\n")
