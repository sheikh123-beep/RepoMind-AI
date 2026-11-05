import requests

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from rag.code_parser import process_repository_files
from services.embedding_service import generate_embeddings, generate_embedding
from agents.orchestrator import AgentOrchestrator
from vectorstore.chroma_service import store_code_chunks, search_code
from services.github_service import (
    analyze_repository,
    parse_github_url,
    get_repository_info,
    get_repository_files,
    download_python_files
)


app = FastAPI(
    title="RepoMind AI",
    description="Intelligent Multi-Agent GitHub Repository Analyst",
    version="1.0.0"
)


# REQUEST MODELS

class RepositoryRequest(BaseModel):
    repo_url: str


class RepositorySearchRequest(BaseModel):
    repo_url: str
    query: str
    n_results: int = 5


class AgentCodeRequest(BaseModel):
    code: str
    file_path: str = "unknown"


class RepositoryQuestionRequest(BaseModel):
    repo_url: str
    question: str
    n_results: int = 5


# HOME

@app.get("/")
def home():
    return {
        "project": "RepoMind AI",
        "message": "Welcome to RepoMind AI!",
        "status": "Running Successfully"
    }


# HEALTH CHECK

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "RepoMind AI"
    }


# REPOSITORY ANALYSIS

@app.post("/api/repository/analyze")
def analyze_repo(request: RepositoryRequest):
    try:
        result = analyze_repository(request.repo_url)
        return {
            "status": "success",
            "repository": result
        }
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except requests.RequestException:
        raise HTTPException(
            status_code=502,
            detail="Unable to fetch repository data from GitHub."
        )


# REPOSITORY SOURCE CODE DOWNLOAD

@app.post("/api/repository/download")
def download_repo_code(request: RepositoryRequest):
    try:
        owner, repo = parse_github_url(request.repo_url)
        info = get_repository_info(owner, repo)
        branch = info["default_branch"]

        files, truncated = get_repository_files(owner, repo, branch)
        downloaded = download_python_files(owner, repo, branch, files)

        return {
            "status": "success",
            "repository": info["full_name"],
            "downloaded_files_count": len(downloaded),
            "files": downloaded,
            "tree_truncated": truncated
        }
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except requests.RequestException:
        raise HTTPException(
            status_code=502,
            detail="Unable to download repository source code."
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to download repository source code: {str(error)}"
        )


# REPOSITORY CODE CHUNKING

@app.post("/api/repository/chunk")
def chunk_repository_code(request: RepositoryRequest):
    try:
        owner, repo = parse_github_url(request.repo_url)
        info = get_repository_info(owner, repo)
        branch = info["default_branch"]

        files, truncated = get_repository_files(owner, repo, branch)
        downloaded = download_python_files(owner, repo, branch, files)
        chunks = process_repository_files(downloaded)

        return {
            "status": "success",
            "repository": info["full_name"],
            "downloaded_files": len(downloaded),
            "total_chunks": len(chunks),
            "chunks": chunks,
            "tree_truncated": truncated
        }
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except requests.RequestException:
        raise HTTPException(
            status_code=502,
            detail="Unable to fetch repository from GitHub."
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to process repository code: {str(error)}"
        )


# REPOSITORY INDEXING

@app.post("/api/repository/index")
def index_repository(request: RepositoryRequest):
    try:
        owner, repo = parse_github_url(request.repo_url)
        info = get_repository_info(owner, repo)
        branch = info["default_branch"]

        files, truncated = get_repository_files(owner, repo, branch)
        downloaded = download_python_files(owner, repo, branch, files)
        chunks = process_repository_files(downloaded)

        valid_chunks = [
            chunk for chunk in chunks
            if chunk.get("content", "").strip()
        ]

        if not valid_chunks:
            raise HTTPException(
                status_code=400,
                detail="No valid code chunks found."
            )

        texts = [chunk["content"] for chunk in valid_chunks]
        embeddings = generate_embeddings(texts)

        stored_count = store_code_chunks(
            valid_chunks,
            embeddings,
            info["full_name"]
        )

        return {
            "status": "success",
            "message": "Repository indexed successfully!",
            "repository": info["full_name"],
            "downloaded_files": len(downloaded),
            "total_chunks": len(valid_chunks),
            "stored_chunks": stored_count,
            "tree_truncated": truncated
        }
    except HTTPException:
        raise
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except requests.RequestException:
        raise HTTPException(
            status_code=502,
            detail="Unable to fetch repository from GitHub."
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Indexing failed: {str(error)}"
        )


# REPOSITORY SEMANTIC SEARCH

@app.post("/api/repository/search")
def search_repository(request: RepositorySearchRequest):
    try:
        if not request.query.strip():
            raise HTTPException(
                status_code=400,
                detail="Search query cannot be empty."
            )

        if not 1 <= request.n_results <= 20:
            raise HTTPException(
                status_code=400,
                detail="n_results must be between 1 and 20."
            )

        owner, repo = parse_github_url(request.repo_url)
        repository = f"{owner}/{repo}"

        query_embedding = generate_embedding(request.query)
        results = search_code(
            query_embedding,
            repository,
            request.n_results
        )

        return {
            "status": "success",
            "repository": repository,
            "query": request.query,
            "results_count": len(results),
            "results": results
        }
    except HTTPException:
        raise
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(error)}"
        )


# MULTI-AGENT CODE ANALYSIS

@app.post("/api/agents/analyze-code")
def analyze_code_with_agents(request: AgentCodeRequest):
    try:
        if not request.code.strip():
            raise HTTPException(
                status_code=400,
                detail="Code cannot be empty."
            )

        orchestrator = AgentOrchestrator()
        result = orchestrator.analyze_code(
            request.code,
            request.file_path
        )

        return {
            "status": "success",
            "message": "Multi-agent code analysis completed!",
            "file_path": request.file_path,
            "analysis": result
        }
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Agent analysis failed: {str(error)}"
        )


# MULTI-AGENT REPOSITORY ANALYSIS

@app.post("/api/agents/analyze-repository")
def analyze_repository_with_agents(request: RepositoryRequest):
    try:
        owner, repo = parse_github_url(request.repo_url)
        info = get_repository_info(owner, repo)
        branch = info["default_branch"]

        files, truncated = get_repository_files(owner, repo, branch)
        downloaded = download_python_files(owner, repo, branch, files)

        orchestrator = AgentOrchestrator()
        result = orchestrator.analyze_repository(downloaded)

        return {
            "status": "success",
            "message": "Multi-agent repository analysis completed!",
            "repository": info["full_name"],
            "analysis": result,
            "downloaded_files": len(downloaded),
            "tree_truncated": truncated
        }
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except requests.RequestException:
        raise HTTPException(
            status_code=502,
            detail="Unable to fetch repository from GitHub."
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Repository agent analysis failed: {str(error)}"
        )


# ==========================================
# REPOSITORY BUG DETECTION
# ==========================================

@app.post("/api/agents/analyze-bugs")
def analyze_repository_bugs(request: RepositoryRequest):

    try:

        # Step 1: Parse GitHub URL

        owner, repo = parse_github_url(request.repo_url)

        # Step 2: Get repository information

        info = get_repository_info(owner, repo)

        branch = info["default_branch"]

        # Step 3: Fetch repository files

        files, truncated = get_repository_files(
            owner,
            repo,
            branch
        )

        # Step 4: Download Python source files

        downloaded = download_python_files(
            owner,
            repo,
            branch,
            files
        )

        if not downloaded:

            raise HTTPException(
                status_code=404,
                detail="No Python files found in this repository."
            )

        # Step 5: Initialize orchestrator

        orchestrator = AgentOrchestrator()

        # Step 6: Analyze repository bugs

        result = orchestrator.analyze_repository_bugs(
            downloaded
        )

        # Step 7: Return complete report

        return {
            "status": "success",
            "message": "Repository bug analysis completed!",
            "repository": info["full_name"],
            "downloaded_files": len(downloaded),
            "tree_truncated": truncated,
            "bug_analysis": result
        }

    except HTTPException:
        raise

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except requests.RequestException:

        raise HTTPException(
            status_code=502,
            detail="Unable to fetch repository data from GitHub."
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Bug detection failed: {str(error)}"
        )


# RAG REPOSITORY QUESTION ANSWERING

@app.post("/api/repository/ask")
def ask_repository_question(request: RepositoryQuestionRequest):
    try:
        if not request.question.strip():
            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty."
            )

        if not 1 <= request.n_results <= 20:
            raise HTTPException(
                status_code=400,
                detail="n_results must be between 1 and 20."
            )

        owner, repo = parse_github_url(request.repo_url)
        repository = f"{owner}/{repo}"

        orchestrator = AgentOrchestrator()
        result = orchestrator.answer_repository_question(
            question=request.question,
            repository=repository,
            n_results=request.n_results
        )

        return result

    except HTTPException:
        raise
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Repository question answering failed: {str(error)}"
        )
