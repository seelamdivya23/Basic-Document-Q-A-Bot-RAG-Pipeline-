import streamlit as st
import os
import json
import time
import shutil   # 🔥 IMPORTANT (for deleting old vector DB)
import speech_recognition as sr

from src.ingestion import load_documents
from src.chunking import split_documents
from src.embedding import get_embeddings
from src.vectorstore import create_vectorstore, load_vectorstore
from src.retrieval import get_retriever
from src.qa import get_qa_chain


# -----------------------------
# HELPERS
# -----------------------------
def typewriter(text):
    placeholder = st.empty()
    typed = ""
    for char in text:
        typed += char
        placeholder.markdown(typed)
        time.sleep(0.005)


def export_txt(chat_history):
    text = ""
    for q, a in chat_history:
        text += f"You: {q}\nBot: {a}\n\n"
    return text


def export_json(chat_history):
    data = [{"question": q, "answer": a} for q, a in chat_history]
    return json.dumps(data, indent=2)


def get_voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Speak now...")
        audio = r.listen(source)

    try:
        return r.recognize_google(audio)
    except:
        return ""


# -----------------------------
# CACHE SYSTEM
# -----------------------------
@st.cache_resource
def load_system():
    embeddings = get_embeddings()
    db = load_vectorstore(embeddings)
    retriever = get_retriever(db, k=2)   # 🔥 reduce noise
    qa = get_qa_chain(retriever)
    return qa


# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Chat with Documents", layout="wide")


# -----------------------------
# SESSION STATE
# -----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "voice_query" not in st.session_state:
    st.session_state.voice_query = ""


# -----------------------------
# SIDEBAR
# -----------------------------
with st.sidebar:
    st.title("📂 Document Manager")

    uploaded_files = st.file_uploader(
        "Upload PDF, TXT, DOCX, CSV",
        accept_multiple_files=True
    )

    if uploaded_files:
        os.makedirs("data", exist_ok=True)

        for file in uploaded_files:
            file_path = os.path.join("data", file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())

        st.success("✅ Uploaded!")

    # 🔥 Multi-document selection
    files = os.listdir("data") if os.path.exists("data") else []
    selected_files = st.multiselect("Select Documents", files, default=files)

    # 🔄 Build Index (FIXED)
    if st.button("🔄 Build Index"):
        with st.spinner("Indexing..."):

            # 🔥 STEP 1: DELETE OLD VECTORSTORE
            if os.path.exists("vectorstore"):
                shutil.rmtree("vectorstore")

            # 🔥 STEP 2: LOAD ONLY SELECTED FILES
            docs = load_documents(selected_files=selected_files)

            if not docs:
                st.error("No documents found!")
            else:
                chunks = split_documents(docs)
                embeddings = get_embeddings()
                create_vectorstore(chunks, embeddings)

                # 🔥 STEP 3: CLEAR CACHE
                st.cache_resource.clear()

                st.success("✅ Index ready!")

    # 🎤 Voice
    if st.button("🎤 Speak"):
        st.session_state.voice_query = get_voice_input()

    # 📥 Export
    st.subheader("📥 Export Chat")

    st.download_button(
        "Download TXT",
        export_txt(st.session_state.chat_history),
        file_name="chat.txt"
    )

    st.download_button(
        "Download JSON",
        export_json(st.session_state.chat_history),
        file_name="chat.json"
    )

    # 🗑️ Clear
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.success("Chat cleared!")


# -----------------------------
# MAIN UI
# -----------------------------
st.title("💬 Chat with your Documents")

# Display chat history
for q, a in st.session_state.chat_history:
    with st.chat_message("user"):
        st.markdown(q)

    with st.chat_message("assistant"):
        st.markdown(a)


# -----------------------------
# INPUT
# -----------------------------
query = st.chat_input("Ask something from your documents...")

# Voice override
if st.session_state.voice_query:
    query = st.session_state.voice_query
    st.session_state.voice_query = ""


# -----------------------------
# RESPONSE
# -----------------------------
if query:
    if not os.path.exists("vectorstore"):
        st.error("⚠️ Please build the index first!")
    else:
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):

                try:
                    qa = load_system()

                    result = qa.invoke({
                        "question": query,
                        "chat_history": st.session_state.chat_history
                    })

                    answer = result.get("answer", "")
                    sources = result.get("source_documents", [])

                    if not sources or "i don't know" in answer.lower():
                        st.markdown("🤖 I don't know based on the given documents.")
                    else:
                        # ⌨️ Typing animation
                        typewriter(answer)

                        # 🎨 Highlight answer
                        st.markdown(
                            f"""
                            <div style="
                                background-color:#1e293b;
                                padding:15px;
                                border-radius:10px;
                                border-left:5px solid #38bdf8;
                                margin-top:10px;
                            ">
                            {answer}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        # ✅ SHOW ONLY MOST RELEVANT SOURCE
                        with st.expander("📚 Source"):
                            top_doc = sources[0]

                            source = top_doc.metadata.get("source", "Unknown")
                            page = top_doc.metadata.get("page", "N/A")

                            st.write(f"📄 {source} (Page: {page})")

                    # Save chat
                    st.session_state.chat_history.append((query, answer))

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
