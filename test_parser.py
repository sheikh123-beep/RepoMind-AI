from rag.code_parser import (
    parse_python_code,
    split_text_into_chunks,
    process_repository_files
)

# Test 1: Python code parsing
python_code = """
def hello():
    print("Hello World")

class Student:
    def study(self):
        print("Studying")
"""

chunks = parse_python_code(
    python_code,
    "test.py"
)

print("\nTEST 1: Python Parsing")

for chunk in chunks:
    print(
        chunk["name"],
        chunk["start_line"],
        chunk["end_line"]
    )

# Test 2: Text chunking
text = "\n".join(
    [f"This is test line number {i}" for i in range(1, 101)]
)

text_chunks = split_text_into_chunks(
    text,
    "README.md",
    chunk_size=200,
    overlap=30
)

print("\nTEST 2: Text Chunking")

for chunk in text_chunks:
    print(
        chunk["file_path"],
        chunk["start_line"],
        chunk["end_line"]
    )

# Test 3: Repository processing
files = [
    {
        "path": "example.py",
        "content": python_code
    },
    {
        "path": "README.md",
        "content": text
    }
]

processed = process_repository_files(files)

print("\nTEST 3: Repository Processing")
print("Total chunks:", len(processed))

print("\nALL TESTS COMPLETED!")