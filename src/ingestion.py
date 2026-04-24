from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
    CSVLoader
)
import os
import re


# -----------------------------
# 🔹 Clean text function
# -----------------------------
def clean_text(text):
    text = re.sub(r'\n+', '\n', text)   # remove extra newlines
    text = re.sub(r'\s+', ' ', text)    # normalize spaces
    return text.strip()


# -----------------------------
# 🔹 Load Documents
# -----------------------------
def load_documents(data_path="data/", selected_files=None):
    documents = []

    if not os.path.exists(data_path):
        print("❌ Data folder not found!")
        return documents

    files = os.listdir(data_path)

    if not files:
        print("⚠️ No files found in data folder!")
        return documents

    for file in files:

        # 🔥 FILTER SELECTED DOCUMENTS
        if selected_files and file not in selected_files:
            continue

        file_path = os.path.join(data_path, file)

        try:
            # -----------------------------
            # 🔹 File type handling
            # -----------------------------
            if file.endswith(".pdf"):
                loader = PyPDFLoader(file_path)

            elif file.endswith(".txt"):
                loader = TextLoader(file_path, encoding="utf-8")

            elif file.endswith(".docx"):
                loader = Docx2txtLoader(file_path)

            elif file.endswith(".csv"):
                loader = CSVLoader(file_path)

            else:
                print(f"⚠️ Skipping unsupported file: {file}")
                continue

            docs = loader.load()

            # -----------------------------
            # 🔥 Clean + Metadata
            # -----------------------------
            for i, doc in enumerate(docs):

                # Clean text
                doc.page_content = clean_text(doc.page_content)

                # Always store filename
                doc.metadata["source"] = file

                # 🔥 PAGE NUMBER FIX
                if "page" in doc.metadata and isinstance(doc.metadata["page"], int):
                    # PDF page fix (0 → 1 indexing)
                    doc.metadata["page"] = doc.metadata["page"] + 1
                else:
                    # TXT / CSV / fallback
                    doc.metadata["page"] = i + 1

                # Optional: add chunk id (helps debugging)
                doc.metadata["chunk_id"] = i

            documents.extend(docs)

        except Exception as e:
            print(f"❌ Error loading {file}: {str(e)}")

    print(f"✅ Total loaded documents: {len(documents)}")
    return documents
