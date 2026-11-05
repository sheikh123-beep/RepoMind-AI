
import ast


class DocumentationAgent:
    """
    Generates documentation for Python classes and functions.
    """

    def __init__(self):
        self.agent_name = "Documentation Agent"

    def analyze(self, code, file_path="unknown"):

        if not isinstance(code, str) or not code.strip():
            raise ValueError("Code cannot be empty.")

        try:
            tree = ast.parse(code)
        except SyntaxError as error:
            return {
                "agent": self.agent_name,
                "file_path": file_path,
                "status": "syntax_error",
                "error": str(error),
                "documentation": []
            }

        documentation = []

        for node in ast.walk(tree):

            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):

                documentation.append({
                    "type": "function",
                    "name": node.name,
                    "description": ast.get_docstring(node) or
                    "No description available.",
                    "parameters": [
                        argument.arg
                        for argument in node.args.args
                    ],
                    "line": node.lineno
                })

            elif isinstance(node, ast.ClassDef):

                documentation.append({
                    "type": "class",
                    "name": node.name,
                    "description": ast.get_docstring(node) or
                    "No description available.",
                    "methods": [
                        item.name
                        for item in node.body
                        if isinstance(
                            item,
                            (ast.FunctionDef, ast.AsyncFunctionDef)
                        )
                    ],
                    "line": node.lineno
                })

        return {
            "agent": self.agent_name,
            "file_path": file_path,
            "status": "success",
            "total_documented_items": len(documentation),
            "documentation": documentation,
            "summary": (
                f"Generated documentation for "
                f"{len(documentation)} items in {file_path}."
            )
        }

