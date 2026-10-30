import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings
from cache.redis_client import RedisCache
from sentence_transformers import util

cache = RedisCache()

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

def get_semantic_response(question, threshold=0.85):
    query_embedding = np.array(embedding_model.embed_query(question))
    pattern = "3ala_damanty:generator_semantic:*"
    
    for key in cache.client.scan_iter(match=pattern):
        stored = cache.get(key)
        if not stored:
            continue
            
        stored_embedding = np.array(stored["embedding"])
        similarity = util.cos_sim(query_embedding, stored_embedding).item()
        
        if similarity >= threshold:
            print("found in cache")
            return stored["response"]

    return None

def save_semantic_response(question, response):
    embedding = embedding_model.embed_query(question)
    key = cache.make_key(namespace="generator_semantic", data=question)
    
    cache.set(
        key,
        {
            "question": question,
            "embedding": embedding,
            "response": response
        },
        ttl=3600
    )
    print("saved in cache")