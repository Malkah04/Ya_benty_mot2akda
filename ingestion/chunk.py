
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import hashlib

def split_documents(
    documents: list[Document],
    file_name:str
) -> list[Document]:
    """Split a list of Documents into smaller chunks."""

    full_txt ="".join([doc.page_content for doc in documents])
    full_hash = hashlib.sha256(full_txt.encode('utf-8')).hexdigest()[:16]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=120,
        separators=["\n\n", "\n", ". ", " ", ""],
        add_start_index=True,
    )

    chunks = splitter.split_documents(documents)

    final_chks =[]
    for i ,chunk in enumerate(chunks):
        chunk_unique_id = f"{full_hash}_chunk_{i}"
        chunk.metadata.update({
            "file_hash":full_hash,
            "file_name":file_name,
            "chunk_id":chunk_unique_id
        })

        final_chks.append(chunk)

    return final_chks
