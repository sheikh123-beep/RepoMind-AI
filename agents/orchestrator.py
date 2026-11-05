
from agents.repository_analyzer import RepositoryAnalyzerAgent
from agents.code_understanding import CodeUnderstandingAgent
from agents.bug_detector import BugDetectionAgent
from agents.documentation_agent import DocumentationAgent

from services.embedding_service import generate_embedding
from services.llm_service import generate_answer

from vectorstore.chroma_service import (
    search_code,
    build_rag_context
)


class AgentOrchestrator:

    def __init__(self):

        self.repository_analyzer = RepositoryAnalyzerAgent()
        self.code_understanding = CodeUnderstandingAgent()
        self.bug_detector = BugDetectionAgent()
        self.documentation_agent = DocumentationAgent()

    # ==========================================
    # REPOSITORY ANALYSIS
    # ==========================================

    def analyze_repository(self, files):

        return self.repository_analyzer.analyze(files)

    # ==========================================
    # CODE ANALYSIS
    # ==========================================

    def analyze_code(self, code, file_path="unknown"):

        understanding = self.code_understanding.analyze(
            code,
            file_path
        )

        bugs = self.bug_detector.analyze(
            code,
            file_path
        )

        documentation = self.documentation_agent.analyze(
            code,
            file_path
        )

        return {
            "repository_analysis": None,
            "code_understanding": understanding,
            "bug_analysis": bugs,
            "documentation": documentation
        }

    # ==========================================
    # COMPLETE REPOSITORY BUG ANALYSIS
    # ==========================================

    def analyze_repository_bugs(self, files):

        if not isinstance(files, list):
            raise ValueError("Files must be provided as a list.")

        file_reports = []

        total_issues = 0

        severity_summary = {
            "high": 0,
            "medium": 0,
            "low": 0
        }

        category_summary = {}

        for file in files:

            if isinstance(file, dict):

                file_path = file.get(
                    "path",
                    file.get("file_path", "unknown")
                )

                code = file.get(
                    "content",
                    file.get("code", "")
                )

            else:
                continue

            if not isinstance(code, str) or not code.strip():
                continue

            # Analyze individual Python file

            try:

                report = self.bug_detector.analyze(
                    code,
                    file_path
                )

                file_reports.append(report)

                total_issues += report["total_issues"]

                for severity, count in report[
                    "severity_summary"
                ].items():

                    severity_summary[severity] += count

                for category, count in report[
                    "category_summary"
                ].items():

                    category_summary[category] = (
                        category_summary.get(category, 0) + count
                    )

            except Exception as error:

                file_reports.append({
                    "agent": "Bug Detection Agent",
                    "file_path": file_path,
                    "status": "error",
                    "total_issues": 0,
                    "issues": [],
                    "error": str(error)
                })

        return {
            "agent": "Bug Detection Agent",
            "status": "success",
            "total_files_scanned": len(file_reports),
            "total_issues": total_issues,
            "severity_summary": severity_summary,
            "category_summary": category_summary,
            "file_reports": file_reports,
            "summary": (
                f"Scanned {len(file_reports)} files and detected "
                f"{total_issues} potential issues."
            )
        }

    # ==========================================
    # RAG RETRIEVAL
    # ==========================================

    def retrieve_repository_context(
        self,
        question,
        repository,
        n_results=5
    ):

        if not question.strip():
            raise ValueError("Question cannot be empty.")

        query_embedding = generate_embedding(question)

        results = search_code(
            query_embedding,
            repository,
            n_results
        )

        context = build_rag_context(results)

        return {
            "question": question,
            "repository": repository,
            "retrieved_chunks": len(results),
            "results": results,
            "context": context
        }

    # ==========================================
    # REPOSITORY QUESTION ANSWERING
    # ==========================================

    def answer_repository_question(
        self,
        question,
        repository,
        n_results=5
    ):

        # Step 1: Retrieve relevant code

        rag_result = self.retrieve_repository_context(
            question,
            repository,
            n_results
        )

        # Step 2: Check retrieved context

        if not rag_result["results"]:

            return {
                "status": "no_context",
                "question": question,
                "repository": repository,
                "answer": (
                    "No relevant code found in the indexed repository."
                ),
                "retrieved_chunks": 0,
                "context": "",
                "sources": []
            }

        # Step 3: Build grounded prompt

        prompt = f"""
You are RepoMind AI, an intelligent GitHub repository analyst.

IMPORTANT RULES:

1. Answer using ONLY the repository code context provided below.
2. Do not invent functions, files, or features.
3. If context is insufficient, clearly say so.
4. Explain in simple language.
5. Mention relevant file names whenever possible.
6. Follow the user's requested answer length.

REPOSITORY:

{repository}

USER QUESTION:

{question}

RETRIEVED REPOSITORY CODE:

{rag_result["context"]}

INSTRUCTIONS:

Analyse the retrieved code and provide an accurate answer.

ANSWER:
"""

        # Step 4: Generate local AI answer

        answer = generate_answer(
            prompt,
            temperature=0.2
        )

        # Step 5: Handle errors

        if answer.startswith("Error:"):

            return {
                "status": "error",
                "question": question,
                "repository": repository,
                "answer": answer,
                "retrieved_chunks": rag_result["retrieved_chunks"]
            }

        # Step 6: Return answer and sources

        return {
            "status": "success",
            "question": question,
            "repository": repository,
            "answer": answer,
            "retrieved_chunks": rag_result["retrieved_chunks"],
            "context": rag_result["context"],
            "sources": [
                result["metadata"]
                for result in rag_result["results"]
            ]
        }

    # ==========================================
    # COMPLETE PROJECT ANALYSIS
    # ==========================================

    def analyze_project(self, files, code, file_path="unknown"):

        repository_report = self.analyze_repository(files)

        code_report = self.analyze_code(
            code,
            file_path
        )

        return {
            "project": "RepoMind AI",
            "status": "success",
            "repository_analysis": repository_report,
            "code_analysis": code_report
        }

