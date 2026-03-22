from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

DATA_PATH = "data/raw"

documents = []

# Load PDFs
for file in os.listdir(DATA_PATH):
    if file.endswith(".pdf"):
        loader = PyPDFLoader(os.path.join(DATA_PATH, file))
        docs = loader.load()
        documents.extend(docs)

print(f"Loaded {len(documents)} pages")

# Split documents into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100
)

chunks = splitter.split_documents(documents)

print(f"Created {len(chunks)} chunks")

# Show sample chunk
print("\nSample chunk:\n")
print(chunks[0].page_content[:400])