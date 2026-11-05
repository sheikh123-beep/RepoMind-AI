# 🧠 RepoMind AI
### Intelligent Multi-Agent GitHub Repository Analyst

RepoMind AI is an AI-powered GitHub repository analysis platform that helps developers understand, explore, and analyze code repositories using AI agents, Retrieval-Augmented Generation (RAG), and Large Language Models (LLMs).

It combines repository analysis, code intelligence, bug detection, and AI-powered code question answering in one interactive dashboard.

## 🚀 Key Features

- **Repository Analysis:** Analyze repository structure, programming languages, file types, and important files.
- **Code Intelligence:** Extract Python functions, classes, imports, and code structure using AST parsing.
- **AI Repository Chat:** Ask natural-language questions about repository code and receive context-aware answers.
- **RAG Pipeline:** Retrieve relevant code chunks using local embeddings and ChromaDB.
- **Multi-Agent Architecture:** Specialized agents for repository analysis, code understanding, documentation, and bug detection.
- **Bug Detection:** Identify potential code-quality issues and security-related patterns.
- **Interactive Dashboard:** Explore analysis results through a Streamlit-based dashboard with charts and metrics.

## 🏗️ Project Architecture

```text
RepoMind-AI/
│
├── agents/
│   ├── repository_analyzer.py
│   ├── code_understanding.py
│   ├── bug_detector.py
│   ├── documentation_agent.py
│   └── orchestrator.py
│
├── backend/
│   └── main.py
│
├── frontend/
│   └── app.py
│
├── rag/
│   └── code_parser.py
│
├── services/
│   ├── github_service.py
│   ├── embedding_service.py
│   └── llm_service.py
│
├── vectorstore/
│   └── chroma_service.py
│
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Backend | FastAPI |
| Frontend | Streamlit |
| AI / LLM | Ollama, Qwen 2.5 (3B) |
| RAG | Retrieval-Augmented Generation |
| Embeddings | Sentence Transformers |
| Vector Database | ChromaDB |
| Code Parsing | Python AST |
| API Integration | GitHub REST API |
| Data Processing | Pandas |

## ⚙️ How It Works

1. User provides a GitHub repository URL.
2. RepoMind AI fetches repository information and source files.
3. The code parser extracts meaningful code structures and creates chunks.
4. Local embedding models generate vector representations.
5. ChromaDB stores the code embeddings.
6. When a user asks a question, relevant code chunks are retrieved.
7. The local LLM generates an answer using the retrieved repository context.
8. Specialized agents provide repository insights and potential bug findings.

## 💻 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/sheikh123-beep/RepoMind-AI.git
cd RepoMind-AI
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root using `.env.example` as a template.

Add your GitHub token if required by the GitHub integration:

```env
GITHUB_TOKEN=your_github_token_here
```

Never upload your actual `.env` file or API credentials to GitHub.

### 5. Install and Start Ollama

Install Ollama and download the model:

```bash
ollama pull qwen2.5:3b
```

Make sure the Ollama service is running before using AI Repository Chat.

### 6. Start the Backend

```bash
python -m uvicorn backend.main:app --reload
```

Backend API:

```text
http://127.0.0.1:8000
```

Swagger Documentation:

```text
http://127.0.0.1:8000/docs
```

### 7. Start the Frontend

Open another terminal:

```bash
python -m streamlit run frontend/app.py
```

The Streamlit dashboard will open in your browser.

## 🔌 Main API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Backend welcome |
| GET | `/health` | Health check |
| POST | `/api/repository/analyze` | Analyze repository |
| POST | `/api/repository/download` | Download repository files |
| POST | `/api/repository/chunk` | Generate code chunks |
| POST | `/api/repository/index` | Index repository |
| POST | `/api/repository/search` | Search code chunks |
| POST | `/api/repository/ask` | AI repository question answering |
| POST | `/api/agents/analyze-code` | Analyze code |
| POST | `/api/agents/analyze-repository` | Multi-agent repository analysis |
| POST | `/api/agents/analyze-bugs` | Detect potential bugs |

## 🧪 Testing

Run the available test scripts:

```bash
python test_parser.py
python test_llm.py
python test_bug_detector.py
python test_repository_analyzer.py
```

## 🔮 Future Improvements

- Cloud deployment with publicly accessible frontend and backend.
- Improved code retrieval and semantic search.
- Support for additional programming languages.
- Advanced static analysis and security checks.
- More specialized AI agents.
- Repository comparison and code quality reports.

## 👨‍💻 Author

**Sheikh Abubakar**

B.Tech Computer Science & Engineering

GitHub: [sheikh123-beep](https://github.com/sheikh123-beep)

---

⭐ If you find RepoMind AI interesting, consider giving this repository a star!