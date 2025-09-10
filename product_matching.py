import sys
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import chromadb
from sentence_transformers import SentenceTransformer
import streamlit as st
from rapidfuzz import process


@st.cache_resource
def init_chromadb():
    chroma_client = chromadb.PersistentClient(path='./chroma_db')
    return chroma_client.get_or_create_collection(name='products')

@st.cache_resource
def get_embedding_model():
    return SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# Product matching functions
def find_product_semantic_match(spoken_text, products, threshold=40.0):
    collection = init_chromadb()
    embedding_model = get_embedding_model()
    
    if not spoken_text:
        return None
    
    try:
        query_embedding = embedding_model.encode(spoken_text).tolist()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3,
            include=["metadatas", "distances"]
        )

        if results and results['metadatas']:
            best_match = results['metadatas'][0][0]
            best_distance = results['distances'][0][0]
            similarity = (1 - best_distance) * 100

            if similarity >= threshold:
                for product in products:
                    if product['name'] == best_match['name']:
                        return product
            else:
                st.warning("Low confidence, another method is being used...")
                return find_product_fuzzy_match(spoken_text, products)

    except Exception as e:
        st.error(f"Error in semantic search: {e}")
        return find_product_fuzzy_match(spoken_text, products)

def find_product_fuzzy_match(spoken_text, products):
    product_names = [p["name"] for p in products]
    best_match = process.extractOne(spoken_text, product_names)

    if best_match:
        matched_name, score, index = best_match
        return products[index]
    return None