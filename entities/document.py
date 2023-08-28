import hashlib


def generate_doc(uploaded_file):
    doc_content = uploaded_file.read().decode()
    m = hashlib.md5()
    m.update(uploaded_file.name.encode('utf-8'))
    uid = m.hexdigest()[:12]
    return Document(uid, doc_content, uploaded_file.name)


class Document:
    def __init__(self, doc_id, text, source):
        self.id = doc_id
        self.text = text
        self.source = source
