from langchain_community.document_loaders import PyPDFLoader,WebBaseLoader,TextLoader ,Docx2txtLoader,UnstructuredPowerPointLoader,WikipediaLoader
from ingestion.audio import load_audio

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
    loader = WikipediaLoader(wiki)
    docs =loader.load()
    return docs



FILE_LOADER = {
    ".pdf": load_pdf,
    ".docx": load_docx,
    ".txt": load_text,
    ".pptx": load_powerpoint,
}
SRC_LOADER ={
    "url": load_url,
    "wikipedia": load_wikipedia,
}
AUDIO_LOADER ={
    ".wav": load_audio
}
