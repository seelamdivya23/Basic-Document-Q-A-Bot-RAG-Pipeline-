def get_retriever(db, k=5):
    return db.as_retriever(
        search_type="mmr",   # 🔥 better than similarity
        search_kwargs={
            "k": k,
            "lambda_mult": 0.7
        }
    )
