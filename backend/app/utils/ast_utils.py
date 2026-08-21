import ast


def parse_python_file(file_path: str):
    """
    Parse a Python file into an AST tree.
    """

    with open(file_path, "r", encoding="utf-8") as file:
        source = file.read()

    return ast.parse(source)