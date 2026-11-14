import re
from rank_bm25 import BM25Okapi

def tokenize(text):
    return re.findall(r"[\w]+(?:[-./][\w]+)*", text.lower())

def build_bm25_index(documents):
    if not documents:
        raise ValueError("The documents list is empty. Cannot build BM25 index.")
    
    tokenized_corpus = [tokenize(doc.page_content) for doc in documents]
    bm25 = BM25Okapi(tokenized_corpus)
    return bm25

