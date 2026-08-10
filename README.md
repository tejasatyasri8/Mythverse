## Live Demo

[Try MythVerse](https://mythverse-seven.vercel.app/)

# MythVerse

**MythVerse** is an AI-powered scripture knowledge assistant that uses **Retrieval-Augmented Generation (RAG)** to answer questions from selected religious texts.

Users can select a religion and scripture, ask questions, and receive responses grounded in the relevant scripture passages retrieved from a vector database.

## 🚀 Live Application

**Frontend:** https://mythverse-seven.vercel.app/

**Backend API:** https://mythverse-backend.onrender.com/

**API Docs:** https://mythverse-backend.onrender.com/docs

---

## 🎯 Project Highlights

* **31,803+ scripture passages** indexed for semantic retrieval
* RAG-based question answering
* Qdrant Cloud vector database
* Semantic vector search with metadata filtering
* Religion + book-level retrieval isolation
* Bhagavad Gita and Bible support
* Google OAuth authentication
* Conversation-based chat interface
* Scripture comparison mode
* Next.js frontend deployed on Vercel
* FastAPI backend deployed on Render
* Production CORS configuration
* Designed to operate within a memory-constrained deployment environment

---

## 🏗️ Architecture

```text
                         ┌─────────────────────┐
                         │        User         │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Next.js Frontend  │
                         │       Vercel        │
                         └──────────┬──────────┘
                                    │
                              POST /chat/
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   FastAPI Backend   │
                         │       Render        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  Query Embedding    │
                         │  Qdrant Inference   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    Qdrant Cloud     │
                         │                     │
                         │ Semantic Retrieval  │
                         │ + Metadata Filters  │
                         └──────────┬──────────┘
                                    │
                             Relevant Passages
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      Groq LLM       │
                         │ Context + Question  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Generated Response  │
                         │   Next.js Frontend  │
                         └─────────────────────┘
```

---

## 🧠 Retrieval-Augmented Generation

MythVerse uses a retrieval-first architecture rather than sending the user's question directly to an LLM.

### RAG Pipeline

```text
User Question
      │
      ▼
Qdrant Cloud Inference
      │
      │  Query Embedding
      ▼
Qdrant Semantic Search
      │
      ├── Religion Filter
      │
      └── Book Filter
      │
      ▼
Top-K Relevant Scripture Passages
      │
      ▼
Context Construction
      │
      ▼
Groq LLM
      │
      ▼
Grounded Response
```

### Why retrieval filtering matters

The vector database stores metadata alongside every scripture passage:

```text
religion
book
chapter
verse
text
```

When a user selects a scripture, the retriever applies both **religion** and **book** filters before returning semantic search results.

For example:

```text
Question:
"What is karma?"

Religion:
Hinduism

Book:
Bhagavad Gita
```

The retrieval system searches for semantically similar passages while restricting results to:

```text
religion = Hinduism
book = Bhagavad Gita
```

This prevents passages from unrelated scripture collections from being returned.

---

## 📚 Current Knowledge Base

MythVerse currently supports:

### Hinduism

**Bhagavad Gita**

* Sanskrit text
* English translation
* Meaning
* Chapter information
* Verse information

### Christianity

**Bible**

* Book/reference
* Chapter
* Verse
* Scripture text

More scripture collections can be added using the same data-processing and embedding pipeline.

---

## 📊 Project Metrics

| Metric              |                      Value |
| ------------------- | -------------------------: |
| Indexed passages    |                **31,803+** |
| Vector dimension    |                    **384** |
| Vector database     |           **Qdrant Cloud** |
| Retrieval           | **Semantic Vector Search** |
| Retrieval filtering |        **Religion + Book** |
| LLM                 |               **Groq API** |
| Backend             |                **FastAPI** |
| Frontend            |        **Next.js + React** |
| Authentication      |           **Google OAuth** |
| Frontend deployment |                 **Vercel** |
| Backend deployment  |                 **Render** |

---

## 🛠️ Technology Stack

### Frontend

* Next.js
* React
* TypeScript
* Tailwind CSS
* NextAuth
* Google OAuth

### Backend

* Python
* FastAPI
* SQLAlchemy
* Pydantic
* Uvicorn

### AI / RAG

* Retrieval-Augmented Generation
* Semantic vector search
* Qdrant inference
* `sentence-transformers/all-MiniLM-L6-v2`
* Groq API

### Database / Infrastructure

* Qdrant Cloud
* SQLite
* Vercel
* Render
* Docker

---

## 📂 Project Structure

```text
Mythverse/
│
├── backend/
│   ├── app/
│   │   ├── database/
│   │   ├── embeddings/
│   │   ├── models/
│   │   ├── retriever/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── vectorstore/
│   │   ├── config.py
│   │   └── main.py
│   │
│   ├── data/
│   ├── scripts/
│   ├── requirements.txt
│   └── runtime.txt
│
├── frontend/
│   └── src/
│       └── app/
│           ├── api/
│           ├── components/
│           ├── hooks/
│           ├── login/
│           ├── services/
│           ├── types/
│           ├── utils/
│           ├── page.tsx
│           └── providers.tsx
│
└── README.md
```

---

## 🔍 Example Retrieval

For the question:

> **What is karma?**

MythVerse generates a query representation and searches Qdrant.

Example retrieved results:

```text
Bhagavad Gita — Chapter 8, Verse 3
Similarity Score: 0.4007

Bhagavad Gita — Chapter 5, Verse 4
Similarity Score: 0.3952
```

The retrieved passages are then supplied to the LLM as context for response generation.

The similarity score is a vector similarity measurement and **is not an accuracy or confidence percentage**.

---

## 🔐 Authentication

MythVerse uses **Google OAuth** through NextAuth.

Authentication flow:

```text
User
 ↓
Google Login
 ↓
NextAuth
 ↓
Authenticated Session
 ↓
MythVerse Chat
```

---

## ☁️ Deployment

The application is deployed as two independent services.

### Frontend

```text
Next.js
    ↓
Vercel
```

### Backend

```text
FastAPI
    ↓
Render
```

### Vector Database

```text
Qdrant Cloud
```

This separation allows the frontend, API server, and vector database to be independently managed and deployed.

---

## ⚙️ Local Development

### Backend

```bash
cd backend

python -m venv venv
```

Activate the environment on Windows:

```powershell
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start FastAPI:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will run at:

```text
http://localhost:3000
```

---

## 🔮 Future Improvements

* Add more scripture collections
* Add verse citations directly to responses
* Improve retrieval ranking and reranking
* Add automated RAG evaluation
* Add retrieval precision/recall metrics
* Add multilingual support
* Add streaming LLM responses
* Improve long-term conversation memory

---

## 👩‍💻 Author

**Teja Satya Sri**

B.Tech — Mechanical Engineering (Robotics)
Minor in Computer Science

Interested in **AI/ML, LLM applications, RAG systems, and intelligent software engineering**.
