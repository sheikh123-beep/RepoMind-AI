
import ast


class CodeUnderstandingAgent:
    """
    Understands Python source code using AST parsing.
    """

    def __init__(self):
        self.agent_name = "Code Understanding Agent"

    def analyze(self, code, file_path="unknown"):
        """
        Analyze Python code and extract structural information.
        """

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
                "summary": "Unable to analyze invalid Python code."
            }

        functions = []
        classes = []
        imports = []

        for node in ast.walk(tree):

            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append({
                    "name": node.name,
                    "start_line": node.lineno,
                    "end_line": getattr(node, "end_lineno", node.lineno),
                    "arguments": [
                        argument.arg for argument in node.args.args
                    ]
                })

            elif isinstance(node, ast.ClassDef):
                classes.append({
                    "name": node.name,
                    "start_line": node.lineno,
                    "end_line": getattr(node, "end_lineno", node.lineno),
                    "methods": [
                        item.name
                        for item in node.body
                        if isinstance(
                            item,
                            (ast.FunctionDef, ast.AsyncFunctionDef)
                        )
                    ]
                })

            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    imports.extend(
                        alias.name for alias in node.names
                    )
                else:
                    imports.append(node.module or "")

        return {
            "agent": self.agent_name,
            "file_path": file_path,
            "status": "success",
            "total_functions": len(functions),
            "total_classes": len(classes),
            "imports": sorted(set(imports)),
            "functions": functions,
            "classes": classes,
            "summary": (
                f"{file_path} contains {len(functions)} functions "
                f"and {len(classes)} classes."
            )
        }

