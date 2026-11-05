import ast
import hashlib


def remove_duplicate_chunks(chunks):
    """
    Remove duplicate chunks based on file path and content.
    """
    unique_chunks = []
    seen = set()

    for chunk in chunks:
        content = chunk.get("content", "").strip()

        if not content:
            continue

        unique_key = (
            chunk.get("file_path", ""),
            chunk.get("type", ""),
            chunk.get("start_line", 0),
            chunk.get("end_line", 0),
            hashlib.md5(content.encode("utf-8")).hexdigest()
        )

        if unique_key not in seen:
            seen.add(unique_key)
            unique_chunks.append(chunk)

    return unique_chunks


def parse_python_code(code, file_path):
    """
    Parse Python source code into meaningful function
    and class chunks with accurate line numbers.
    """

    chunks = []
    lines = code.splitlines()

    try:
        tree = ast.parse(code)

        for node in ast.walk(tree):

            if isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                    ast.ClassDef
                )
            ):
                start_line = node.lineno
                end_line = getattr(
                    node,
                    "end_lineno",
                    start_line
                )

                content = "\n".join(
                    lines[start_line - 1:end_line]
                )

                if not content.strip():
                    continue

                chunks.append({
                    "file_path": file_path,
                    "name": node.name,
                    "type": type(node).__name__,
                    "start_line": start_line,
                    "end_line": end_line,
                    "content": content
                })

    except SyntaxError:
        return []

    chunks.sort(
        key=lambda chunk: (
            chunk["start_line"],
            chunk["end_line"]
        )
    )

    return remove_duplicate_chunks(chunks)


def split_text_into_chunks(
    text,
    file_path,
    chunk_size=1000,
    overlap=150
):
    """
    Split text into meaningful chunks while preserving
    accurate start and end line numbers.
    """

    chunks = []

    if not text or not text.strip():
        return chunks

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size"
        )

    lines = text.splitlines()

    start_index = 0

    while start_index < len(lines):

        current_content = []
        current_size = 0
        end_index = start_index

        while end_index < len(lines):

            line = lines[end_index]
            line_size = len(line) + 1

            if (
                current_content
                and current_size + line_size > chunk_size
            ):
                break

            current_content.append(line)
            current_size += line_size
            end_index += 1

            # Prevent an infinite loop for very long lines.
            if current_size >= chunk_size:
                break

        content = "\n".join(current_content).strip()

        if content:
            chunks.append({
                "file_path": file_path,
                "type": "text",
                "start_line": start_index + 1,
                "end_line": end_index,
                "content": content
            })

        if end_index >= len(lines):
            break

        # Calculate overlap using characters.
        next_start = end_index
        overlap_size = 0

        while next_start > start_index and overlap_size < overlap:
            next_start -= 1
            overlap_size += len(lines[next_start]) + 1

        start_index = max(next_start, start_index + 1)

    return remove_duplicate_chunks(chunks)


def process_repository_files(files):
    """
    Process downloaded repository files and remove
    duplicate chunks.
    """

    all_chunks = []

    for file in files:

        file_path = file["path"]
        content = file["content"]

        if not content or not content.strip():
            continue

        if file_path.lower().endswith(".py"):

            chunks = parse_python_code(
                content,
                file_path
            )

            # Fallback for Python files without functions/classes.
            if not chunks:
                chunks = split_text_into_chunks(
                    content,
                    file_path
                )

        else:
            chunks = split_text_into_chunks(
                content,
                file_path
            )

        all_chunks.extend(chunks)

    return remove_duplicate_chunks(all_chunks)