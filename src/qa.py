from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

def get_qa_chain(retriever):
    
    llm = OllamaLLM(model="phi3")

    prompt_template = """
    You are a helpful AI assistant.

    Answer the question ONLY using the provided context.
    If the answer is not in the context, say:
    "I don't know based on the given documents."

    Context:
    {context}

    Question:
    {question}

    Answer:
    """

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )

    return qa_chain
