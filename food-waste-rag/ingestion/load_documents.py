from langchain_community.document_loaders import PyPDFLoader
import os

DATA_PATH = "data/raw"

documents = []

for file in os.listdir(DATA_PATH):
    if file.endswith(".pdf"):
        loader = PyPDFLoader(os.path.join(DATA_PATH, file))
        docs = loader.load()
        documents.extend(docs)

print(f"Loaded {len(documents)} pages from PDFs")

print(documents[0].page_content[:500])