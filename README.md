<<<<<<< HEAD
=======
[README.md](https://github.com/user-attachments/files/25383064/README.md)
>>>>>>> 3edfcd84c03aaa1b2704a6cdcface1e05b13e58b
# Code KT Generator

An AI-powered tool that automatically generates **Knowledge Transfer (KT) documents** from source code. Point it at a Git repository or upload a ZIP of your codebase, and it produces structured documentation to help teams onboard developers, hand off projects, or preserve institutional knowledge.

---

## Features

- **Dual upload modes** — provide a Git repository URL or upload a ZIP archive
- **Python code analysis** — parses source files to extract functions, classes, modules, and relationships
- **RAG-based generation** — uses Retrieval-Augmented Generation with vector embeddings for accurate, context-aware documentation
- **KT document output** — generates human-readable Knowledge Transfer documents ready for sharing
- **Session management** — stores upload history and generated documents in a database

---

## Architecture

```
code-KT-generator/
├── backend/                    # Python + FastAPI
│   ├── main.py                 # API entry point & route definitions
│   ├── models.py               # Database models (SQLAlchemy/Pydantic)
│   ├── database.py             # Database connection setup
│   ├── curd.py                 # CRUD operations
│   ├── analyzer/
│   │   └── python_analyzer.py  # AST-based Python code analysis
│   ├── rag/
│   │   └── embeddings.py       # Vector embedding pipeline (RAG)
│   ├── generators/
│   │   ├── doc_generator.py    # Documentation generator
│   │   └── kt_generator.py     # KT document generator
│   ├── requirements.txt
│   └── .env.example
└── frontend/                   # Next.js + React
    ├── app/                    # Next.js App Router pages
    ├── package.json
    └── postcss.config.js
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15, React 19, Tailwind CSS |
| Backend | Python 3.13, FastAPI |
| Database | SQLite / PostgreSQL (via SQLAlchemy) |
| AI / Embeddings | OpenAI API (embeddings + chat completion) |
| Code Analysis | Python AST |

---

## Prerequisites

- Python 3.10+
- Node.js 18+
- An OpenAI API key (or compatible LLM provider)

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/code-KT-generator.git
cd code-KT-generator
```

### 2. Backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your API key(s)

# Start the API server
uvicorn main:app --reload
```

The backend runs at `http://localhost:8000`.
Interactive API docs are available at `http://localhost:8000/docs`.

### 3. Frontend

```bash
cd frontend

npm install
npm run dev
```

The frontend runs at `http://localhost:3000`.

---

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in the required values:

```env
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=sqlite:///./kt_generator.db
```

---

## Usage

1. Open the app at `http://localhost:3000`
2. Choose an upload method:
   - **Git URL** — paste the URL of a public (or accessible) Git repository
   - **ZIP Upload** — upload a ZIP archive of your codebase
3. Submit and wait for the analysis to complete
4. Download or view the generated KT document

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/upload/git` | Ingest a codebase from a Git URL |
| `POST` | `/upload/zip` | Ingest a codebase from a ZIP file |
| `GET`  | `/sessions` | List all KT generation sessions |
| `GET`  | `/sessions/{id}` | Get a specific session and its document |
| `POST` | `/generate/{id}` | Trigger KT document generation for a session |

> Verify exact endpoint paths in `backend/main.py`.

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## License

MIT
