from langchain_huggingface import HuggingFaceEmbeddings
from langchain_classic.embeddings import CacheBackedEmbeddings
from langchain_community.storage import RedisStore
# from cache.redis_client import redis_client
import redis

redis_client = redis.Redis(host="localhost",port=6379,db=1,decode_responses=False)

def create_embedding_model():
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
 
    store =RedisStore(client =redis_client ,namespace="embedding_cache")

    cached_embedding_model = CacheBackedEmbeddings.from_bytes_store(
        underlying_embeddings=embedding_model,
        document_embedding_cache=store,
        namespace=embedding_model.model_name,
        query_embedding_cache=True
    )

    return cached_embedding_model

