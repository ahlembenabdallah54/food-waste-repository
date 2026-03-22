from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_classic.chains import RetrievalQA
import os
from langchain.prompts import PromptTemplate

prompt_template = """
You are a food waste sustainability assistant.

Use the provided context to answer the question.

At the end of the answer include a section called:

Recommended Actions:
Provide 3-5 practical steps organizations can take.

Context:
{context}

Question:
{question}
"""

PROMPT = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question"]
)
# Load embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Load vector database
vectorstore = FAISS.load_local(
    "vector_db",
    embeddings,
    allow_dangerous_deserialization=True
)

retriever = vectorstore.as_retriever()

# Local LLM (Ollama)
llm = ChatOllama(
    model="llama3",
    temperature=0
)

# RAG pipeline
qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type_kwargs={"prompt": PROMPT},
    return_source_documents=True

)

while True:
    query = input("\nAsk a question about food waste: ")

    if query.lower() == "exit":
        break

    result = qa.invoke(query)

    print("\nAnswer:\n")
    print(result["result"])

    print("\nSources:")

    for doc in result["source_documents"]:
        source = doc.metadata.get("source", "Unknown document")
        print("-", source)