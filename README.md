# RAGMind AI

**RAGMind AI** - AI that retrieves knowledge before it answers.

FastAPI backend with streaming responses, FAISS vector search, and a ChatGPT-style frontend.

Currently using **Bhagavata Purana** as the demo knowledge base. You can replace it with any PDFs or text files to build your own domain-specific chatbot.

> BETA: Under active development

## Demo

[![RAGMind AI Demo](https://img.youtube.com/vi/KG0ktySviAM/maxresdefault.jpg)](https://youtu.be/KG0ktySviAM)

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| LLM | NVIDIA AI Endpoints (Llama 4 Maverick) via LangChain |
| Embeddings | NVIDIA NeMo Retriever |
| Vector Store | FAISS |
| Backend | FastAPI, Uvicorn, LangChain, Python |
| Frontend | HTML / CSS / JS with SSE streaming |
| Config | Pydantic Settings, python-dotenv |

---

## Setup

**1. Install dependencies**

```bash
git clone https://github.com/MeetSolanki530/ragmind.git
cd ragmind/backend
pip install -r requirements.txt
```

**2. Add your `.env` file in `backend/`**

```env
NVIDIA_API_KEY=your_nvidia_api_key
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
MODEL_NAME=meta/llama-4-maverick-17b-128e-instruct
EMBEDDING_MODEL=nvidia/llama-3.2-nemoretriever-300m-embed-v1
VECTOR_DB=faiss
VECTOR_STORE_PATH=vector_store
MAX_CONTEXT_CHUNKS=4
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

**3. Ingest documents**

Put your files in `data/documents/` and run:

```bash
python scripts/ingest_documents.py
```

**4. Start the server**

```bash
python app/main.py
```

Open http://localhost:8080

---

## Project Structure

```
backend/
  .env
  requirements.txt
  app/
    main.py
    api/chat.py
    config/settings.py
    config/prompts.py
    rag/pipeline.py
    rag/retriever.py
    rag/embeddings.py
    services/llm_service.py
    utils/text_chunker.py
  scripts/
    ingest_documents.py
data/documents/
frontend/
  index.html
  static/css/style.css
  static/js/app.js
vector_store/index.faiss
```

---

## Future Plans

- MongoDB for chat history persistence
- User authentication and session management
- Multi-document collection support
- File upload from the UI

