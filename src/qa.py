from langchain_ollama import OllamaLLM
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory


def get_qa_chain(retriever):

    llm = OllamaLLM(
        model="phi3",
        temperature=0
    )

    memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key="answer"
)


    prompt_template = """
    You are a strict document-based assistant.

    Your job is to answer ONLY using the provided context.

    Rules:
    - Do NOT use external knowledge
    - Do NOT guess
    - If answer is not clearly present, say:
      "I don't know based on the given documents."

    Chat History:
    {chat_history}

    Context:
    {context}

    Question:
    {question}

    Answer (be clear and concise):
    """

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["chat_history", "context", "question"]
    )

    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": prompt}
    )

    return qa_chain
