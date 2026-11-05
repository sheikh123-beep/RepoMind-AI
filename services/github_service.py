import os
import re
import requests

from urllib.parse import urlparse, quote
from dotenv import load_dotenv

load_dotenv()

GITHUB_API = "https://api.github.com"

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "RepoMind-AI"
}

if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"


# -----------------------------------------
# STEP 1: Parse GitHub Repository URL
# -----------------------------------------

def parse_github_url(repo_url: str):

    parsed = urlparse(repo_url.strip())

    if parsed.scheme not in ("http", "https"):
        raise ValueError("Please provide a valid GitHub URL.")

    if parsed.netloc.lower() not in ("github.com", "www.github.com"):
        raise ValueError("Only GitHub repository URLs are supported.")

    parts = parsed.path.strip("/").split("/")

    if len(parts) != 2:
        raise ValueError(
            "URL format must be: https://github.com/owner/repository"
        )

    owner, repo = parts

    if repo.endswith(".git"):
        repo = repo[:-4]

    if not re.fullmatch(r"[A-Za-z0-9_.-]+", owner):
        raise ValueError("Invalid GitHub username.")

    if not re.fullmatch(r"[A-Za-z0-9_.-]+", repo):
        raise ValueError("Invalid repository name.")

    return owner, repo


# -----------------------------------------
# STEP 2: Get Repository Information
# -----------------------------------------

def get_repository_info(owner: str, repo: str):

    url = f"{GITHUB_API}/repos/{owner}/{repo}"

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=20
    )

    if response.status_code == 404:
        raise ValueError("Repository not found or is private.")

    if response.status_code == 403:
        raise ValueError(
            "GitHub API rate limit exceeded or access denied."
        )

    response.raise_for_status()

    return response.json()


# -----------------------------------------
# STEP 3: Get Repository File Tree
# -----------------------------------------

def get_repository_files(owner: str, repo: str, branch: str):

    encoded_branch = quote(branch, safe="")

    url = (
        f"{GITHUB_API}/repos/{owner}/{repo}"
        f"/git/trees/{encoded_branch}"
    )

    response = requests.get(
        url,
        headers=HEADERS,
        params={"recursive": "1"},
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    ignored_dirs = {
        "node_modules",
        "venv",
        ".venv",
        ".git",
        "__pycache__",
        "dist",
        "build"
    }

    files = []

    for item in data.get("tree", []):

        if item.get("type") != "blob":
            continue

        path = item["path"]

        if any(
            part in ignored_dirs
            for part in path.split("/")
        ):
            continue

        files.append({
            "path": path,
            "size": item.get("size", 0)
        })

    return files, data.get("truncated", False)


# -----------------------------------------
# STEP 4: Download Python Source Files
# -----------------------------------------

def download_python_files(owner, repo, branch, files):

    downloaded_files = []

    python_files = [
        file for file in files
        if file["path"].lower().endswith(".py")
        and file.get("size", 0) <= 500_000
    ][:10]

    for file in python_files:

        path = file["path"]

        encoded_branch = quote(branch, safe="/")
        encoded_path = quote(path, safe="/")

        raw_url = (
            f"https://raw.githubusercontent.com/"
            f"{owner}/{repo}/{encoded_branch}/{encoded_path}"
        )

        try:

            response = requests.get(
                raw_url,
                headers={"User-Agent": "RepoMind-AI"},
                timeout=20
            )

            response.raise_for_status()

            downloaded_files.append({
                "path": path,
                "content": response.text
            })

        except requests.RequestException:
            continue

    return downloaded_files


# -----------------------------------------
# STEP 5: Complete Repository Analysis
# -----------------------------------------

def analyze_repository(repo_url: str):

    owner, repo = parse_github_url(repo_url)

    info = get_repository_info(owner, repo)

    branch = info["default_branch"]

    files, truncated = get_repository_files(
        owner,
        repo,
        branch
    )

    python_files = [
        file for file in files
        if file["path"].lower().endswith(".py")
    ]

    return {
        "name": info["name"],
        "full_name": info["full_name"],
        "description": info["description"],
        "language": info["language"],
        "stars": info["stargazers_count"],
        "forks": info["forks_count"],
        "default_branch": branch,
        "total_files": len(files),
        "python_files_count": len(python_files),
        "python_files": python_files,
        "files": files,
        "tree_truncated": truncated
    }