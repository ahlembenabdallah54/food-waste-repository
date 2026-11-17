# Food Waste RAG – Intelligent Food Waste Information Assistant

An AI-powered Retrieval-Augmented Generation (RAG) application designed to provide reliable information about food waste, waste management, and environmental regulations.

The system combines Large Language Models (LLMs), semantic search, and document retrieval to answer users' questions using information extracted from PDF documents.

## Project Overview

Food Waste RAG is an intelligent question-answering system that allows users to interact with a knowledge base of food-waste-related documents.

Instead of generating answers using only an LLM's internal knowledge, the application retrieves relevant document passages and uses them as context to generate grounded responses.

## Key Features

- **Document Ingestion:** Upload PDF documents to enrich the knowledge base.
- **Intelligent Document Processing:** Extract, split, and process document content.
- **Semantic Search:** Retrieve relevant information using vector embeddings.
- **RAG Pipeline:** Generate context-aware answers using retrieved document passages.
- **Source References:** Display the sources supporting generated answers.
- **Confidence Information:** Provide confidence information with responses.
- **OCR Support:** Process scanned PDF documents using Tesseract OCR.

## System Architecture

The application follows a Retrieval-Augmented Generation architecture.

1. **Document ingestion:** PDF files are uploaded and their content is extracted.
2. **Text processing:** Documents are divided into smaller chunks.
3. **Embedding generation:** Text chunks are transformed into numerical vectors.
4. **Vector storage:** FAISS stores the embeddings for efficient similarity search.
5. **Retrieval:** Relevant document chunks are retrieved based on the user's question.
6. **Answer generation:** Groq-hosted LLM generates an answer using the retrieved context.
7. **Response:** The frontend displays the answer, sources, and confidence information.

## Technologies Used

| Component | Technologies |
|---|---|
| Frontend | Vue.js, Vite |
| Backend | Python, FastAPI |
| RAG Framework | LangChain |
| Vector Database | FAISS |
| Embedding Model | sentence-transformers/all-MiniLM-L6-v2 |
| LLM Provider | Groq |
| Language Model | openai/gpt-oss-20b |
| Document Processing | PyPDF, Tesseract OCR |
| Environment Management | Python Virtual Environment, dotenv |

## Project Structure

```text
food-waste-repository/
│
├── food-waste-rag/
│   ├── app/
│   ├── backend/
│   │   ├── main.py
│   │   └── requirements.txt
│   │
│   ├── data/
│   ├── evaluation/
│   ├── frontend/
│   ├── ingestion/
│   ├── rag/
│   ├── vector_db/
│   │
│   └── .env
│
├── .gitignore
└── README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/ahlembenabdallah54/food-waste-repository.git

cd food-waste-repository/food-waste-rag
```

### 2. Backend Setup

Create and activate a virtual environment:

```bash
python -m venv venv
```

On Windows:

```bash
venv\Scripts\activate
```

Install the backend dependencies:

```bash
pip install -r backend/requirements.txt
```

### 3. Environment Variables

Create a `.env` file inside the `food-waste-rag` directory:

```env
GROQ_API_KEY=your_groq_api_key
```

Replace the placeholder with your own Groq API key.

**Important:** Never upload your `.env` file or API key to GitHub.

### 4. Run the Backend

Open a terminal inside the `backend` directory:

```bash
cd backend
```

Start FastAPI:

```bash
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Backend URL:

`http://localhost:8000`

API documentation:

`http://localhost:8000/docs`

### 5. Run the Frontend

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Frontend URL:

`http://localhost:5173`

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Check API status |
| POST | `/upload` | Upload and process PDF documents |
| GET | `/documents` | Retrieve the list of available documents |
| POST | `/ask` | Ask questions and receive RAG-generated answers |

## Current Knowledge Base

The current indexed knowledge base includes:

- 8 PDF documents.
- 2,265 processed text chunks.
- Documents covering food waste and waste-management topics.
- Tunisian waste legislation, including `tunisia_waste_law.pdf`.

## Project Objective

The main objective is to demonstrate how Retrieval-Augmented Generation can transform document collections into an interactive knowledge assistant, providing more relevant and source-grounded answers in the food waste domain.

---

**Project:** Food Waste RAG  
**Category:** Artificial Intelligence | Natural Language Processing | Retrieval-Augmented Generation  
**Repository:** [GitHub – food-waste-repository](https://github.com/ahlembenabdallah54/food-waste-repository)
