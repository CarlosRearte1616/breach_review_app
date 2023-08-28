from tiktoken import get_encoding


class DocumentAnalyzer:
    def __init__(self):
        self.tokenizer = get_encoding('cl100k_base')

    def estimate_token_count(self, text):
        token_counts = len(self.tokenizer.encode(
            text,
            disallowed_special=()))
        return token_counts
