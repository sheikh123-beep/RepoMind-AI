
import ast
import re


class BugDetectionAgent:
    """
    Detects common potential issues in Python source code.

    This is a lightweight static analysis agent.
    It does not replace professional security auditing tools.
    """

    def __init__(self):
        self.agent_name = "Bug Detection Agent"

    # ==========================================
    # ISSUE CREATION
    # ==========================================

    def create_issue(
        self,
        issue_type,
        line,
        message,
        severity,
        category,
        recommendation
    ):

        return {
            "type": issue_type,
            "line": line,
            "message": message,
            "severity": severity,
            "category": category,
            "recommendation": recommendation
        }

    # ==========================================
    # AST ANALYSIS
    # ==========================================

    def analyze_ast(self, tree):

        issues = []

        for node in ast.walk(tree):

            # Dangerous eval() and exec()

            if isinstance(node, ast.Call):

                if isinstance(node.func, ast.Name):

                    if node.func.id == "eval":

                        issues.append(
                            self.create_issue(
                                "Dangerous Function",
                                node.lineno,
                                "Use of eval() can execute arbitrary code.",
                                "high",
                                "Security",
                                "Avoid eval(). Use safer alternatives such as "
                                "ast.literal_eval() when appropriate."
                            )
                        )

                    elif node.func.id == "exec":

                        issues.append(
                            self.create_issue(
                                "Dangerous Function",
                                node.lineno,
                                "Use of exec() can execute arbitrary code.",
                                "high",
                                "Security",
                                "Avoid exec() and use explicit functions "
                                "or safer alternatives."
                            )
                        )

            # Bare except detection

            if isinstance(node, ast.ExceptHandler):

                if node.type is None:

                    issues.append(
                        self.create_issue(
                            "Bare Exception",
                            node.lineno,
                            "Bare except may hide unexpected errors.",
                            "medium",
                            "Code Quality",
                            "Catch specific exceptions instead of using "
                            "a bare except block."
                        )
                    )

            # Mutable default arguments

            if isinstance(
                node,
                (ast.FunctionDef, ast.AsyncFunctionDef)
            ):

                defaults = node.args.defaults

                all_defaults = (
                    defaults + node.args.kw_defaults
                )

                for default in all_defaults:

                    if isinstance(
                        default,
                        (ast.List, ast.Dict, ast.Set)
                    ):

                        issues.append(
                            self.create_issue(
                                "Mutable Default Argument",
                                node.lineno,
                                (
                                    f"Function '{node.name}' uses "
                                    "a mutable default argument."
                                ),
                                "medium",
                                "Code Quality",
                                "Use None as the default value and "
                                "create the mutable object inside "
                                "the function."
                            )
                        )

        return issues

    # ==========================================
    # PATTERN ANALYSIS
    # ==========================================

    def analyze_patterns(self, lines):

        issues = []

        patterns = [
            {
                "pattern": r"\bTODO\b",
                "type": "Incomplete Code",
                "message": "TODO comment indicates unfinished work.",
                "severity": "low",
                "category": "Code Quality",
                "recommendation": "Complete or remove the TODO item."
            },
            {
                "pattern": r"\bFIXME\b",
                "type": "Potential Bug",
                "message": "FIXME comment indicates code requiring attention.",
                "severity": "medium",
                "category": "Code Quality",
                "recommendation": "Review and resolve the marked issue."
            },
            {
                "pattern": (
                    r"""(?i)\b(?:password|passwd|secret|api_key|access_token)\b\s*=\s*['"][^'"]+['"]"""
                ),
                "type": "Possible Hardcoded Secret",
                "message": "Possible hardcoded credential detected.",
                "severity": "high",
                "category": "Security",
                "recommendation": (
                    "Move credentials to environment variables "
                    "and never commit real secrets to Git."
                )
            }
        ]

        for line_number, line in enumerate(lines, start=1):

            stripped = line.strip()

            if not stripped:
                continue

            is_comment = stripped.startswith("#")

            for item in patterns:

                # Detect TODO and FIXME inside comments.

                if item["type"] in (
                    "Incomplete Code",
                    "Potential Bug"
                ):

                    if not is_comment:
                        continue

                # Ignore comments for hardcoded secret detection.

                elif is_comment:
                    continue

                if re.search(item["pattern"], line):

                    issues.append(
                        self.create_issue(
                            item["type"],
                            line_number,
                            item["message"],
                            item["severity"],
                            item["category"],
                            item["recommendation"]
                        )
                    )

        return issues

    # ==========================================
    # MAIN ANALYSIS
    # ==========================================

    def analyze(self, code, file_path="unknown"):

        if not isinstance(code, str) or not code.strip():

            raise ValueError("Code cannot be empty.")

        issues = []

        lines = code.splitlines()

        # Syntax validation

        try:

            tree = ast.parse(code)

        except SyntaxError as error:

            issues.append(
                self.create_issue(
                    "Syntax Error",
                    error.lineno or 1,
                    error.msg,
                    "high",
                    "Syntax",
                    "Fix the Python syntax error before executing the file."
                )
            )

            return self.generate_report(
                file_path,
                issues,
                status="syntax_error"
            )

        # AST-based analysis

        issues.extend(
            self.analyze_ast(tree)
        )

        # Line-based pattern analysis

        issues.extend(
            self.analyze_patterns(lines)
        )

        return self.generate_report(
            file_path,
            issues,
            status="success"
        )

    # ==========================================
    # REPORT GENERATION
    # ==========================================

    def generate_report(
        self,
        file_path,
        issues,
        status="success"
    ):

        severity_counts = {
            "high": 0,
            "medium": 0,
            "low": 0
        }

        category_counts = {}

        for issue in issues:

            severity = issue["severity"]

            severity_counts[severity] = (
                severity_counts.get(severity, 0) + 1
            )

            category = issue["category"]

            category_counts[category] = (
                category_counts.get(category, 0) + 1
            )

        return {
            "agent": self.agent_name,
            "file_path": file_path,
            "status": status,
            "total_issues": len(issues),
            "severity_summary": severity_counts,
            "category_summary": category_counts,
            "issues": issues,
            "summary": (
                f"Found {len(issues)} potential issues "
                f"in {file_path}."
            )
        }
