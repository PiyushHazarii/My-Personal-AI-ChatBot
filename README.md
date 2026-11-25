# Piyush AI — Personal AI Chatbot (RAG + Qdrant)

A dedicated personal AI chatbot named **Piyush AI** that answers questions **exclusively** about Piyush Hazari using his personal documents (Resume, CBSE 10th Marksheet, CBSE 12th Marksheet, and GitHub Portfolio Knowledge Base).

---

## 1. Technology Stack

### Backend
- **Python 3.10+**
- **FastAPI**: High-performance asynchronous API framework.
- **Qdrant Vector Database**: Cloud vector database for semantic similarity search.
- **Sentence Transformers (`all-MiniLM-L6-v2`)**: Generates 384-dimensional dense vector embeddings.
- **Groq API / OpenAI API**: High-speed LLM inference (`openai/gpt-oss-120b` or `openai/gpt-oss-20b`).
- **pypdf & python-docx**: Document extraction from PDF and text documents.

### Frontend
- **React 19 + Vite**: Ultra-fast modern frontend development.
- **Lucide React**: Clean icons for a modern conversational interface.
- **Responsive Custom CSS**: High-contrast dark theme, quick suggestion chips, message timestamps, verified source tags, and dynamic typing indicator.

---

## 2. Project Structure

```text
Piyush AI/
├── backend/
│   ├── data/                                         # Personal source documents
│   │   ├── 10th Marksheet.txt                        # CBSE Class 10 marksheet
│   │   ├── 12th Marksheet.txt                        # CBSE Class 12 marksheet
│   │   ├── Piyush-Resume.pdf                         # Verified professional resume
│   │   └── piyush_github_portfolio_knowledge_base.txt # Repositories & project details
│   ├── config.py                                     # Environment & configuration settings
│   ├── document_loader.py                            # PDF/TXT extraction, text cleaning & chunking
│   ├── vector_db.py                                  # Qdrant client & SentenceTransformer management
│   ├── rag.py                                        # Strict boundary enforcement & LLM generation
│   ├── ingest.py                                     # Standalone ingestion pipeline runner
│   ├── main.py                                       # FastAPI server endpoints (/health, /chat, /ingest)
│   └── requirements.txt                              # Backend Python dependencies
├── frontend/                                         # React + Vite application
│   ├── src/
│   │   ├── App.jsx                                   # Chatbot interface & state management
│   │   ├── App.css                                   # Styling, glowing accents & animations
│   │   ├── index.css                                 # Typography & reset
│   │   └── main.jsx                                  # React entry point
│   ├── index.html                                    # App title & metadata
│   └── package.json                                  # Frontend dependencies
├── .env                                              # Environment variables (API keys & Qdrant credentials)
├── .env.example                                      # Template environment variables
└── README.md                                         # Complete documentation & run instructions
```

---

## 3. Strict Chatbot Boundaries & Guardrails

Piyush AI strictly respects the following domain boundaries:

1. **Exclusive Domain**: Answers questions **only** about Piyush Hazari (education, GPA, CBSE marks, technical skills, projects, contact information).
2. **Strict Factual Grounding**: Relies **only** on retrieved chunks from verified documents. No assumptions or hallucinations.
3. **Missing Info Protection**: If information is unavailable in the documents:
   > *"I don't have this information about Piyush Hazari in my knowledge base."*
4. **Immediate Rejection of Unrelated Queries**: General knowledge, coding requests, trivia, math questions, and unrelated conversations are rejected:
   > *"I am Piyush AI, a specialized assistant exclusively dedicated to Piyush Hazari. I can only answer questions related to Piyush Hazari's education, skills, projects, and personal background."*
5. **Prompt Injection Immunity**: Rejects prompt jailbreaks, roleplay instructions, or attempts to override system rules.

---

## 4. Complete Execution Flow (Step-by-Step)

```
[User Question]
       │
       ▼
[React Frontend (App.jsx)] ───► POST /chat ───► [FastAPI Backend]
                                                      │
                                                      ├─► [1. Guardrail Check]
                                                      │    Rejects non-Piyush / injection prompts immediately
                                                      │
                                                      ├─► [2. Embed Query]
                                                      │    SentenceTransformer("all-MiniLM-L6-v2")
                                                      │
                                                      ├─► [3. Semantic Search]
                                                      │    Qdrant Cloud (collection: piyush_ai_knowledge)
                                                      │
                                                      ├─► [4. Retrieve Top Context & Sources]
                                                      │    (Resume, Marksheets, GitHub Portfolio)
                                                      │
                                                      ├─► [5. Prompt LLM via Groq API]
                                                      │    Factual grounding + strict instructions
                                                      │
                                                      ▼
                                           [ChatResponse: answer + sources]
                                                      │
       ┌──────────────────────────────────────────────┘
       ▼
[Render in UI with Source Badges & Timestamps]
```

---

## 5. How to Run the Application

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### Step 1: Environment Variables
Create or verify your `.env` file in `Piyush AI/.env`:

```env
GROQ_API_KEY=gsk_your_groq_api_key_here
QDRANT_URL=https://your-cluster-url.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_COLLECTION_NAME=piyush_ai_knowledge
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
GROQ_MODEL=openai/gpt-oss-120b
```

---

### Step 2: Ingest the Personal Documents
To parse the PDF and TXT files, chunk them, compute embeddings, and store them into Qdrant:

```bash
cd "D:\Piyush_AI_Engineer\Piyush AI"
python -m backend.ingest
```

Expected output:
```text
Total chunks extracted across all documents: 162
- 10th Marksheet.txt (CBSE 10th Marksheet): 3 chunks
- 12th Marksheet.txt (CBSE 12th Marksheet): 4 chunks
- Piyush-Resume.pdf (Professional Resume): 6 chunks
- piyush_github_portfolio_knowledge_base.txt: 149 chunks
INGESTION COMPLETE: 162 points stored in Qdrant!
```

---

### Step 3: Run the FastAPI Backend Server

```bash
cd "D:\Piyush_AI_Engineer\Piyush AI"
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend will be active at:
- **API Health**: `http://127.0.0.1:8000/health`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`

---

### Step 4: Run the React Frontend

Open a new terminal window:

```bash
cd "D:\Piyush_AI_Engineer\Piyush AI\frontend"
npm run dev
```

The frontend will run at:
- **Chatbot Web UI**: `http://localhost:5173`

---

## 6. API Reference

### 1. `GET /health`
Verifies backend status, Qdrant connectivity, and indexed point count.

**Response:**
```json
{
  "status": "healthy",
  "service": "Piyush AI Backend",
  "qdrant_status": "connected",
  "collection": "piyush_ai_knowledge",
  "indexed_points": 162,
  "embedding_model": "all-MiniLM-L6-v2",
  "llm_model": "openai/gpt-oss-120b"
}
```

### 2. `POST /chat`
Accepts a user question and conversation history, executes RAG retrieval, and returns the strictly grounded answer.

**Request:**
```json
{
  "message": "What is Piyush's college and GPA?",
  "history": []
}
```

**Response:**
```json
{
  "answer": "Piyush Hazari is pursuing a B.Tech in Computer Science & Engineering at Gandhi Institute Of Excellent Technocrats (GIET), Bhubaneswar (2022–2026) with a GPA of 8.1.",
  "sources": [
    "Piyush-Resume.pdf"
  ]
}
```

### 3. `POST /ingest`
Triggers an on-demand re-ingestion of documents located in `backend/data/`.
