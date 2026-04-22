from langchain_community.vectorstores import FAISS
import os

def create_vectorstore(chunks, embeddings):
    db = FAISS.from_documents(chunks, embeddings)
    db.save_local("vectorstore")
    return db

def load_vectorstore(embeddings):
    return FAISS.load_local(
        "vectorstore",
        embeddings,
        allow_dangerous_deserialization=True
    )
