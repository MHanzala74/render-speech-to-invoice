import chromadb
from sentence_transformers import SentenceTransformer
import streamlit as st

# Initialize ChromaDB
@st.cache_resource
def init_chromadb():
    chroma_client = chromadb.PersistentClient(path='./chroma_db')
    return chroma_client.get_or_create_collection(name='products')

@st.cache_resource
def get_embedding_model():
    return SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# Store products in ChromaDB
def store_products_in_chromedb(products):
    collection = init_chromadb()
    embedding_model = get_embedding_model()
    
    if collection.count() == 0:
        st.info("Saving products to ChromaDB...")
        documents, metadatas, ids, embeddings = [], [], [], []

        for product in products:
            search_text = f"{product['name']} {product.get('productDescription', '')}"
            embedding = embedding_model.encode(search_text).tolist()

            documents.append(search_text)
            metadatas.append({
                "name": product["name"],
                "price": str(product.get("price", 0)),
                "uoM": product.get("uoM", "pcs"),
                "taxRate": product.get("taxRate", "0%")
            })
            ids.append(product["id"])
            embeddings.append(embedding)

        batch_size = 50
        for i in range(0, len(documents), batch_size):
            collection.add(
                documents=documents[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size],
                ids=ids[i:i+batch_size],
                embeddings=embeddings[i:i+batch_size]
            )
        st.success(f"{len(products)} products saved")