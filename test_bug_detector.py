
from agents.bug_detector import BugDetectionAgent

agent = BugDetectionAgent()

sample_code = """
password = "my_secret_password"

def calculate_total(items=[]):
    return eval("10 + 20")

def execute_code():
    exec("print('Hello')")

def handle_error():
    try:
        print("Testing")
    except:
        pass

# TODO: Improve this function
# FIXME: Handle invalid input
"""

result = agent.analyze(
    sample_code,
    file_path="sample.py"
)

print("\n========== BUG DETECTION REPORT ==========\n")

print("Agent:", result["agent"])
print("File:", result["file_path"])
print("Status:", result["status"])

print("\nTotal Issues:", result["total_issues"])

print("\nSeverity Summary:")

for severity, count in result["severity_summary"].items():
    print(f"{severity.upper()}: {count}")

print("\nCategory Summary:")

for category, count in result["category_summary"].items():
    print(f"{category}: {count}")

print("\nDetected Issues:")

for issue in result["issues"]:

    print("\n----------------------------")

    print("Type:", issue["type"])
    print("Line:", issue["line"])
    print("Severity:", issue["severity"])
    print("Category:", issue["category"])
    print("Message:", issue["message"])
    print("Recommendation:", issue["recommendation"])

print("\n========== TEST COMPLETED ==========")

