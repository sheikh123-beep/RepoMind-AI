
from collections import Counter
from pathlib import Path


class RepositoryAnalyzerAgent:
    """
    Advanced GitHub repository analyzer.

    Analyzes:
    - Repository structure
    - Programming languages
    - File extensions
    - Project type
    - Important files
    - File categories
    - Project insights
    """

    def __init__(self):

        self.agent_name = "Repository Analyzer Agent"

        self.important_files = [
            "README.md",
            "requirements.txt",
            "pyproject.toml",
            "package.json",
            "Dockerfile",
            "docker-compose.yml",
            "main.py",
            "app.py",
            "manage.py",
            "Cargo.toml",
            "go.mod"
        ]

        self.language_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".jsx": "React",
            ".tsx": "React TypeScript",
            ".java": "Java",
            ".cpp": "C++",
            ".c": "C",
            ".go": "Go",
            ".rs": "Rust",
            ".php": "PHP",
            ".rb": "Ruby",
            ".html": "HTML",
            ".css": "CSS",
            ".sql": "SQL",
            ".swift": "Swift",
            ".kt": "Kotlin",
            ".cs": "C#",
            ".sh": "Shell",
            ".ipynb": "Jupyter Notebook"
        }

    # ================================================
    # FILE CATEGORY DETECTION
    # ================================================

    def categorize_file(self, file_path):

        path = Path(file_path)
        name = path.name.lower()
        extension = path.suffix.lower()

        if (
            "test" in name
            or "tests" in path.parts
            or "__tests__" in path.parts
        ):
            return "Tests"

        if extension in [".md", ".rst", ".txt"]:
            return "Documentation"

        if extension in [
            ".json", ".yaml", ".yml", ".toml",
            ".ini", ".cfg", ".env", ".xml"
        ]:
            return "Configuration"

        if extension in [
            ".py", ".js", ".ts", ".jsx", ".tsx",
            ".java", ".cpp", ".c", ".go", ".rs",
            ".php", ".rb", ".swift", ".kt", ".cs"
        ]:
            return "Source Code"

        if extension in [".png", ".jpg", ".jpeg", ".svg"]:
            return "Assets"

        return "Other"

    # ================================================
    # PROJECT TYPE DETECTION
    # ================================================

    def detect_project_type(self, file_paths):

        file_names = {
            Path(file_path).name.lower()
            for file_path in file_paths
        }

        extensions = {
            Path(file_path).suffix.lower()
            for file_path in file_paths
        }

        project_types = []

        if "requirements.txt" in file_names or "pyproject.toml" in file_names:
            project_types.append("Python Project")

        if "manage.py" in file_names:
            project_types.append("Django Project")

        if "package.json" in file_names:
            project_types.append("Node.js Project")

        if "next.config.js" in file_names or "next.config.ts" in file_names:
            project_types.append("Next.js Project")

        if "vite.config.js" in file_names or "vite.config.ts" in file_names:
            project_types.append("Vite Project")

        if ".ipynb" in extensions:
            project_types.append("Data Science / Jupyter Project")

        if "cargo.toml" in file_names:
            project_types.append("Rust Project")

        if "go.mod" in file_names:
            project_types.append("Go Project")

        if "dockerfile" in file_names:
            project_types.append("Dockerized Project")

        if not project_types:
            project_types.append("General Software Project")

        return project_types

    # ================================================
    # PROJECT INSIGHTS
    # ================================================

    def generate_insights(
        self,
        total_files,
        languages,
        categories,
        important_files,
        project_types
    ):

        insights = []

        if total_files > 0:
            insights.append(
                f"Repository contains {total_files} files."
            )

        if languages:

            primary_language = languages.most_common(1)[0]

            insights.append(
                f"{primary_language[0]} is the most represented "
                f"programming language with {primary_language[1]} files."
            )

        if categories.get("Tests", 0) > 0:

            insights.append(
                f"Repository contains {categories['Tests']} test-related files."
            )

        else:

            insights.append(
                "No test-related files were detected by filename or folder."
            )

        if "README.md" in important_files:

            insights.append(
                "README documentation is available."
            )

        else:

            insights.append(
                "README.md was not detected."
            )

        insights.append(
            "Detected project types: " + ", ".join(project_types)
        )

        return insights

    # ================================================
    # MAIN ANALYSIS
    # ================================================

    def analyze(self, files):

        if not isinstance(files, list):
            raise ValueError("Files must be provided as a list.")

        file_paths = []

        for file in files:

            if isinstance(file, str):

                file_path = file

            elif isinstance(file, dict):

                file_path = file.get("path", "")

                # Ignore directories if type is provided.
                if file.get("type") == "dir":
                    continue

            else:
                continue

            if isinstance(file_path, str) and file_path.strip():

                normalized_path = file_path.replace("\\", "/").strip("/")

                if normalized_path:
                    file_paths.append(normalized_path)

        # Remove duplicate paths.
        file_paths = list(dict.fromkeys(file_paths))

        total_files = len(file_paths)

        # File extensions.
        extensions = Counter(
            Path(file_path).suffix.lower()
            for file_path in file_paths
            if Path(file_path).suffix
        )

        # Programming languages.
        languages = Counter()

        for extension, count in extensions.items():

            language = self.language_map.get(extension)

            if language:
                languages[language] += count

        # Important project files.
        important_files = [
            file_path
            for file_path in file_paths
            if Path(file_path).name.lower()
            in {
                name.lower()
                for name in self.important_files
            }
        ]

        # Folder structure.
        folders = set()
        root_folders = set()

        for file_path in file_paths:

            parts = Path(file_path).parts

            if len(parts) > 1:

                for index in range(1, len(parts)):

                    folders.add(
                        "/".join(parts[:index])
                    )

                root_folders.add(parts[0])

        # File categories.
        categories = Counter(
            self.categorize_file(file_path)
            for file_path in file_paths
        )

        # Project type.
        project_types = self.detect_project_type(file_paths)

        # Top programming languages.
        top_languages = [
            {
                "language": language,
                "files": count
            }
            for language, count in languages.most_common(5)
        ]

        # Insights.
        insights = self.generate_insights(
            total_files,
            languages,
            categories,
            important_files,
            project_types
        )

        # Summary.
        summary = (
            f"Repository contains {total_files} files "
            f"across {len(folders)} folders. "
            f"Detected project type: {', '.join(project_types)}."
        )

        return {

            "agent": self.agent_name,

            "total_files": total_files,

            "total_folders": len(folders),

            "file_extensions": dict(extensions),

            "languages": dict(languages),

            "top_languages": top_languages,

            "project_types": project_types,

            "file_categories": dict(categories),

            "important_files": important_files,

            "root_folders": sorted(root_folders),

            "folder_structure": sorted(folders),

            "insights": insights,

            "summary": summary
        }

