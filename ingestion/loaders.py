from langchain_community.document_loaders import PyPDFLoader,WebBaseLoader,TextLoader ,Docx2txtLoader,UnstructuredPowerPointLoader,WikipediaLoader
from ingestion.audio import load_audio

import requests
from langchain_core.documents import Document

def load_pdf(file):
    loader = PyPDFLoader(file)
    docs =loader.load()
    return docs

def load_docx(file):
    loader = Docx2txtLoader(file)
    docs =loader.load()
    return docs

def load_text(file):
    loader = TextLoader(file)
    docs =loader.load()
    return docs

def load_powerpoint(file):
    loader = UnstructuredPowerPointLoader(file)
    docs =loader.load()
    return docs
    

def load_url(url):
    loader = WebBaseLoader(url)
    docs =loader.load()
    return docs

def load_wikipedia(wiki):
    url = "https://en.wikipedia.org/w/api.php"
    headers = {
        "User-Agent": "3alaDamanty/1.0 (Educational RAG Project)"
    }
    try:
        response = requests.get(
            url,
            params={
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": wiki,
                "srlimit": 5
            },
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        results = response.json().get("query", {}).get("search", [])

        documents = []

        for result in results:
            title = result["title"]

            page_response = requests.get(
                url,
                params={
                    "action": "query",
                    "format": "json",
                    "prop": "extracts",
                    "explaintext": 1,
                    "titles": title
                },
                headers=headers,
                timeout=30
            )

            page_response.raise_for_status()
            pages = page_response.json().get("query", {}).get("pages", {})

            for page in pages.values():
                content = page.get("extract", "").strip()

                if content:
                    documents.append(
                        Document(
                            page_content=content[:10000],
                            metadata={"title": title}
                        )
                    )

        return documents

    except Exception as e:
        print(f"WIKIPEDIA ERROR: {repr(e)}")
        raise
FILE_LOADER = {
    ".pdf": load_pdf,
    ".docx": load_docx,
    ".txt": load_text,
    ".pptx": load_powerpoint,
}
SRC_LOADER ={
    "url": load_url,
}
AUDIO_LOADER ={
    ".wav": load_audio
}
WIKI_LOADER ={
    "wikipedia": load_wikipedia,
}
