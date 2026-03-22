from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os, shutil, math

load_dotenv("../.env")

retriever   = None
vectorstore = None
llm         = None
embeddings_model = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global retriever, vectorstore, llm, embeddings_model
    print("Loading models...")
    embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.load_local("../vector_db", embeddings_model, allow_dangerous_deserialization=True)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0
    )
    print("✅ Models loaded with Groq!")
    yield

app = FastAPI(title="FoodWise AI API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Schemas ──────────────────────────────────────────────────────────────────
class QueryRequest(BaseModel):
    question: str
    lang: str = "en"

class SourceDoc(BaseModel):
    source: str
    snippet: str
    score: float

class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceDoc]
    confidence: float

class UploadResponse(BaseModel):
    filename: str
    chunks: int
    message: str

LANG_INSTRUCTIONS = {
    "en": "Answer in English. Be concise and practical.",
    "fr": "Réponds en français. Sois concis et pratique.",
    "ar": "أجب باللغة العربية. كن موجزاً وعملياً.",
}

def distance_to_score(distance: float) -> float:
    try:
        d = float(distance)
        return round(max(0.0, min(100.0, (1 - d / 4) * 100)), 1)
    except:
        return 0.0

# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "FoodWise AI API is running ⚡ Groq"}

@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    global vectorstore, retriever

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    # Save PDF to data/raw/
    upload_dir = "../data/raw"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Load and chunk the PDF
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)

    if not chunks:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF.")

    # Add to existing FAISS vectorstore
    vectorstore.add_documents(chunks)
    vectorstore.save_local("../vector_db")

    # Update retriever
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    print(f"✅ Added {len(chunks)} chunks from {file.filename}")
    return UploadResponse(
        filename=file.filename,
        chunks=len(chunks),
        message=f"Successfully added {len(chunks)} chunks to the knowledge base!"
    )

@app.get("/documents")
def list_documents():
    """List all uploaded PDF documents."""
    upload_dir = "../data/raw"
    if not os.path.exists(upload_dir):
        return {"documents": []}
    files = [f for f in os.listdir(upload_dir) if f.endswith(".pdf")]
    return {"documents": files, "total": len(files)}

@app.post("/ask", response_model=QueryResponse)
def ask(body: QueryRequest):
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    lang_instruction = LANG_INSTRUCTIONS.get(body.lang, LANG_INSTRUCTIONS["en"])
    docs_with_scores = vectorstore.similarity_search_with_score(body.question, k=4)

    docs   = [d for d, _ in docs_with_scores]
    scores = [distance_to_score(s) for _, s in docs_with_scores]
    confidence = round(sum(scores) / len(scores), 1) if scores else 0.0

    context = "\n\n".join([doc.page_content for doc in docs])

    response = llm.invoke(f"""You are a helpful assistant specialising in food waste reduction.
{lang_instruction}
Use only the provided context to answer.

Context:
{context}

Question: {body.question}

Answer:""")

    sources = [
        SourceDoc(
            source=doc.metadata.get("source", f"Document {i+1}"),
            snippet=doc.page_content[:120],
            score=scores[i]
        )
        for i, doc in enumerate(docs)
    ]
    return QueryResponse(answer=response.content, sources=sources, confidence=confidence)