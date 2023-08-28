class Chunk:
    def __init__(self, chunk_id, text, source, token_size, char_size):
        self.id = chunk_id
        self.text = text
        self.source = source
        self.token_size = token_size
        self.char_size = char_size

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'source': self.source,
            'token_size': self.token_size,
            'char_size': self.char_size,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            chunk_id=data['id'],
            text=data['text'],
            source=data['source'],
            token_size=data['token_size'],
            char_size=data['char_size'],
        )
