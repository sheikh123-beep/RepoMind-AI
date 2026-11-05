
from agents.repository_analyzer import RepositoryAnalyzerAgent


agent = RepositoryAnalyzerAgent()

sample_files = [
    {"path": "README.md", "type": "file"},
    {"path": "requirements.txt", "type": "file"},
    {"path": "main.py", "type": "file"},
    {"path": "app.py", "type": "file"},
    {"path": "agents/orchestrator.py", "type": "file"},
    {"path": "agents/repository_analyzer.py", "type": "file"},
    {"path": "tests/test_main.py", "type": "file"},
    {"path": "frontend/app.py", "type": "file"},
    {"path": "frontend/style.css", "type": "file"},
    {"path": "config/settings.json", "type": "file"},
    {"path": "docs/guide.md", "type": "file"}
]

result = agent.analyze(sample_files)

print("\n========== REPOMIND AI ANALYSIS ==========\n")

print("Total Files:", result["total_files"])

print("Total Folders:", result["total_folders"])

print("\nProject Types:")
print(result["project_types"])

print("\nProgramming Languages:")
print(result["languages"])

print("\nTop Languages:")
print(result["top_languages"])

print("\nFile Categories:")
print(result["file_categories"])

print("\nImportant Files:")
print(result["important_files"])

print("\nRoot Folders:")
print(result["root_folders"])

print("\nProject Insights:")

for insight in result["insights"]:
    print("-", insight)

print("\nSummary:")
print(result["summary"])

print("\n========== TEST COMPLETED ==========")

