class ChunkRepository:
    def __init__(self, datastore):
        self.datastore = datastore

    def save_chunk(self, chunk):
        self.datastore.save_chunk(chunk)
