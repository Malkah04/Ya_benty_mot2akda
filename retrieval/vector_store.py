from langchain_chroma import Chroma
from retrieval.embedding import create_embedding_model

def create_vb():
    embedding_model = create_embedding_model()
    vector_store = Chroma(
        collection_name="3ala_damanty",
        embedding_function=embedding_model,
        persist_directory="./chroma_db"
    )

    return vector_store

def save_chunks(chunks ,ids):
    if len(chunks) != len(ids):
        raise ValueError("Each chunk must have exactly one ID.")
    
    vector_store = create_vb()
    if chunks:
        file_name = chunks[0].metadata.get("file_name")
        if file_name:
            exist = vector_store.get(where={"file_name":file_name})
            if exist and exist["ids"]:
                vector_store.delete(ids=exist["ids"])


    vector_store.add_documents(
        documents=chunks,
        ids=ids
    )
    return vector_store