from langchain_core.tools import tool
from retrieval.retriever import retriever
from retrieval.bm25_index import build_bm25_index , tokenize
from agents.llm import llm
from retrieval.vector_store import create_vb
from sentence_transformers import CrossEncoder

bm25_index = None
bm25_documents = []

def configure_retrieval_resources(bm25, documents ):
    global bm25_index, bm25_documents
    bm25_index = bm25
    bm25_documents = documents


@tool
def semantic_search(query: str,top_k: int = 5,file_name: str = None,content_type: str = None) -> list:
    """
    Search the vector database for semantically
    relevant document chunks.

    Args:
        query: Search query.
        top_k: Maximum number of results.
        file_name: Optional document name filter.
        content_type: Optional content type filter (text/table).
    """

    r = retriever(k=top_k)
    filters = {}

    if file_name: filters["file_name"] = file_name
    if content_type: filters["content_type"] = content_type
    if filters: r.search_kwargs["filter"] = filters
    results = r.invoke(query)

    return [
        {
            "content": doc.page_content,
            "metadata": doc.metadata
        }
        for doc in results
    ]

@tool
def keyword_search(query:str, top_k :int = 5) -> list:
    """
    Search documents using keyword-based retrieval.
    Useful for exact terms, names, and technical identifiers.
    """
    query =tokenize(query)

    if not query:
        raise ValueError("The query is empty after tokenization. Please provide a valid query.")

    scores =bm25_index.get_scores(query)
    ranked_indices = scores.argsort()[::-1]

    r =[]

    for i in ranked_indices:
        score =float(scores[i])

        if score <=0 :
            continue

        r.append({
            "content": bm25_documents[i].page_content,
            "metadata": bm25_documents[i].metadata,
            "bm25_score": score
        })
        if len(r)==top_k:
            break
        
    return r



@tool
def rewrite_query(query: str, chat_history: str) -> str:
    """
    Rewrite the user's query using conversation context.

    Use this tool when the query is ambiguous, contains
    unresolved references, or needs clarification for retrieval.
    """

    prompt = f"""
    You are a query rewriting assistant.

    Your task is to rewrite the original query using
    the provided conversation context.

    Rules:
    - Preserve the original intent.
    - Resolve ambiguous references using the context.
    - Make the query clear and specific for document retrieval.
    - Do not answer the question.
    - If the query is already clear, return it unchanged.
    - Do not introduce information that is not supported
      by the context.

    Conversation Context:
    {chat_history}

    Original Query:
    {query}

    Rewritten Query:
    """

    response = llm.invoke(prompt)

    return response.content.strip()

@tool
def metadata_filter(file_name: str) -> str:
    """
    Retrieve all document chunks belonging to a specific file.

    Use this tool when the user explicitly asks to search
    within a particular document.
    """
    vector_store = create_vb()

    results = vector_store.get(
        where={"file_name": file_name},
        include=["documents", "metadatas"]
    )

    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])

    if not documents:
        return f"No chunks found for file: {file_name}"

    formatted_results = []

    for content, metadata in zip(documents, metadatas):
        formatted_results.append(
            f"""
            "content": {content},
            "metadata": {metadata},
            File: {metadata.get('file_name')}
            Chunk ID: {metadata.get('chunk_id')}
            "file_hash": {metadata.get("file_hash")}
            """
        )
    return "\n---\n".join(formatted_results)


ranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def rerank_results(query: str, results: list ,top_k:int =5) -> list:
    """
    Rerank retrieved document chunks according to their
    relevance to the user's query using a Cross-Encoder.

    Use this after semantic or keyword retrieval.
    """

    pairs =[(query ,result["content"]) for result in results]
    scores =ranker.predict(pairs)

    ranked_results = []

    for result, score in zip(results, scores):
        ranked_result = {
            **result,
            "rerank_score": float(score)
        }
        ranked_results.append(ranked_result)

    ranked_results.sort(
        key=lambda item: item["rerank_score"],
        reverse=True
    )
    return ranked_results[:top_k]


def context_selector(results: list[dict],max_chunks: int = 5,max_chars: int = 12000,max_chunks_per_file: int = 3) -> list[dict]:
    """
    Select a compact and diverse set of relevant chunks.

    Selection considers:
    - Reranker score
    - Duplicate chunks
    - Maximum chunks per file
    - Total context size

    This is an internal pipeline function.
    """

    selected = []
    seen_chunks = set()
    file_counts = {}

    total_chars = 0

    ranked_results = sorted(
        results,
        key=lambda item: item.get("rerank_score", 0),
        reverse=True
    )

    for result in ranked_results:

        content = result.get("content", "")
        metadata = result.get("metadata", {})

        chunk_id = (
            result.get("chunk_id")
            or metadata.get("chunk_id")
        )

        file_name = (
            result.get("file_name")
            or metadata.get("file_name")
            or "unknown"
        )

        if chunk_id and chunk_id in seen_chunks:
            continue

        if file_counts.get(file_name, 0) >= max_chunks_per_file:
            continue

        content_length = len(content)
        if total_chars + content_length > max_chars:
            continue

        selected.append(result)

        if chunk_id:
            seen_chunks.add(chunk_id)

        file_counts[file_name] = (file_counts.get(file_name, 0) + 1)

        total_chars += content_length

        if len(selected) >= max_chunks:
            break

    return selected



@tool
def rerank_results_tool(query: str,results: list[dict],top_k: int = 5) -> list[dict]:
    """
    Rerank retrieved chunks according to their relevance
    to the user's query using a Cross-Encoder.
    """

    return rerank_results(
        query=query,
        results=results,
        top_k=top_k
    )


@tool
def context_selector_tool(results: list[dict],max_chunks: int = 5,max_chars: int = 12000) -> list[dict]:
    """
    Select the most relevant and diverse chunks
    while respecting the context size limit.
    """

    return context_selector(
        results=results,
        max_chunks=max_chunks,
        max_chars=max_chars
    )


tools =[
    context_selector_tool,
    rerank_results_tool,
    semantic_search,
    keyword_search,
    rewrite_query,
    metadata_filter
]