from retrieval.vector_store import create_vb
def retriever(k=3):
    vector_store = create_vb()
    retriver =vector_store.as_retriever(search_kwargs={"k":k})
    return retriver
