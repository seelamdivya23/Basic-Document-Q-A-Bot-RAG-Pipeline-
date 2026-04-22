from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
    CSVLoader
)
import os
import re


# 🔹 Clean text function
def clean_text(text):
    text = re.sub(r'\n+', '\n', text)   # remove extra newlines
    text = re.sub(r'\s+', ' ', text)    # normalize spaces
    return text.strip()


def load_documents(data_path="data/"):
    documents = []

    for file in os.listdir(data_path):
        file_path = os.path.join(data_path, file)

        if file.endswith(".pdf"):
            loader = PyPDFLoader(file_path)

        elif file.endswith(".txt"):
            loader = TextLoader(file_path)

        elif file.endswith(".docx"):
            loader = Docx2txtLoader(file_path)

        elif file.endswith(".csv"):
            loader = CSVLoader(file_path)

        else:
            print(f"⚠️ Skipping unsupported file: {file}")
            continue

        docs = loader.load()

        # 🔥 Apply cleaning + assign metadata
        for i, doc in enumerate(docs):
            doc.page_content = clean_text(doc.page_content)

            # Always store source filename
            doc.metadata["source"] = file

            # 🔥 Smart page handling
            if "page" in doc.metadata:
                # PDF/DOCX already have page numbers
                doc.metadata["page"] = doc.metadata["page"]
            else:
                # TXT/CSV → assign logical page number
                doc.metadata["page"] = i + 1

        documents.extend(docs)

    print(f"✅ Total loaded documents: {len(documents)}")
    return documents
