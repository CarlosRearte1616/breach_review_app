from abc import ABC, abstractmethod
from entities.chunk import Chunk

class Datastore(ABC):
    @abstractmethod
    def save_chunk(self, chunk: Chunk):
        pass