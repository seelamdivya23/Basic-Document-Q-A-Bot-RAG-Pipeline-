from src.ingestion import load_documents
from src.chunking import split_documents
from src.embedding import get_embeddings
from src.vectorstore import create_vectorstore, load_vectorstore
from src.retrieval import get_retriever
from src.qa import get_qa_chain
import os


def index_data():
    print("\n[1/4] Loading documents...")
    docs = load_documents()

    if not docs:
        print("❌ No documents found in 'data/' folder.")
        return

    print(f"✅ Loaded {len(docs)} documents")

    print("\n[2/4] Splitting into chunks...")
    chunks = split_documents(docs)
    print(f"✅ Created {len(chunks)} chunks")

    print("\n[3/4] Creating embeddings...")
    embeddings = get_embeddings()

    print("\n[4/4] Saving vector database...")
    create_vectorstore(chunks, embeddings)

    print("\n🎉 Indexing complete! Vector DB saved.\n")


def run_chat():
    if not os.path.exists("vectorstore"):
        print("❌ Vectorstore not found. Please run indexing first.")
        return

    print("🔄 Loading embeddings and vector database...")
    embeddings = get_embeddings()
    db = load_vectorstore(embeddings)

    retriever = get_retriever(db)
    qa = get_qa_chain(retriever)

    print("\n💬 Ask your questions (type 'exit' to quit)\n")

    while True:
        query = input("You: ")

        if query.lower() == "exit":
            print("👋 Exiting chat...")
            break

        try:
            result = qa.invoke({"query": query})

            sources = result.get("source_documents", [])
            answer = result.get("result", "")

            # 🔥 FINAL LOGIC (important)
            if not sources or "i don't know" in answer.lower():
                print("\n🤖 I don't know based on the given documents.\n")
            else:
                print("\n🤖 Answer:\n", answer)

                print("\n📚 Sources:")
                for doc in sources:
                    source = doc.metadata.get("source", "Unknown")
                    page = doc.metadata.get("page", "N/A")
                    print(f"- {source} (Page: {page})")

            print("\n" + "-" * 50)

        except Exception as e:
            print("❌ Error:", str(e))


if __name__ == "__main__":
    print("Choose an option:")
    print("1. Index Documents")
    print("2. Start Chat")

    choice = input("Enter choice (1/2): ")

    if choice == "1":
        index_data()
    elif choice == "2":
        run_chat()
    else:
        print("❌ Invalid choice")