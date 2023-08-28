class DocumentSplitter:
    def __init__(self, text_splitter):
        self.text_splitter = text_splitter

    def split_document(self, document):
        chunks = self.text_splitter.split_text(document.text)
        return chunks

    def split_text(self, text):
        chunks = self.text_splitter.split_text(text)
        return chunks
