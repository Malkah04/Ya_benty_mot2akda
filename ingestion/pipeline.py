from ingestion.loaders import FILE_LOADER,SRC_LOADER,AUDIO_LOADER ,WIKI_LOADER
from ingestion.chunk import split_documents
from pathlib import Path
from retrieval.vector_store import save_chunks

def ingest(source ,source_type):
    if source_type == "file":
        extension = Path(source).suffix.lower()
        handler = FILE_LOADER.get(extension)
    elif source_type == "audio" :
        extension = Path(source).suffix.lower()
        handler = AUDIO_LOADER.get(extension)
    elif source_type =="url" :
        handler = SRC_LOADER.get(source_type)

    elif source_type =="wikipedia":
        handler = WIKI_LOADER.get(source_type)
    else :
        handler =None
        print("errorrr")

    if handler is None:
        raise ValueError("Unsupported source type")

    documents = handler(source)
    file_name = str(source)

    chunks = split_documents(documents ,file_name)

    ids =[chunk.metadata["chunk_id"] for chunk in chunks]

    save_chunks(chunks ,ids)
    print(f"Successfully ingested {len(chunks)} chunks from {source}.")

    return chunks

