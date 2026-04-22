def get_retriever(db, k=3):
    return db.as_retriever(search_kwargs={"k": k})
