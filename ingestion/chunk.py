from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import hashlib

from sqlalchemy import table

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

    text_docs =[]
    table_docs =[]
    for doc in documents:
        category = doc.metadata.get("category")
        if category == "table":
            print(f"LOGS : Found table document in {file_name}")
            table_docs.append(doc)
        else:
            text_docs.append(doc)

    text_chunks = splitter.split_documents(text_docs)

    final_chks =[]
    for i ,chunk in enumerate(text_chunks):
        chunk_unique_id = f"{full_hash}_chunk_{i}"
        chunk.metadata.update({
            "file_hash":full_hash,
            "file_name":file_name,
            "chunk_id":chunk_unique_id,
            "content_type": "text"
        })

        final_chks.append(chunk)

    for i ,chunk in enumerate(table_docs):
        chunk_unique_id = f"{full_hash}_table_{i}"
        table_content = chunk.metadata.get("text_as_html")
        if not table_content:
            table_content = chunk.page_content

        table_doc = Document(
            page_content=table_content,
            metadata={
                **{
                    k: v for k, v in table.metadata.items()
                    if isinstance(v, (str, int, float, bool))
                },
                "file_hash": full_hash,
                "file_name": file_name,
                "chunk_id": f"{full_hash}_table_{i}",
                "content_type": "table"
            }
        )

        final_chks.append(table_doc)

    return final_chks
