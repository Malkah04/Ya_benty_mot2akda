from langchain_core.documents import Document
import whisper

def load_audio(file_path):
    model = whisper.load_model("base")
    result = model.transcribe(file_path)
    text = result["text"]
    
    return [Document(page_content=text, metadata={"source": file_path})]