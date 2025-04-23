"""Check that all Python files include a module-level docstring."""

import ast
import sys


def has_module_docstring(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read())
            return bool(ast.get_docstring(tree))
        except SyntaxError:
            return False


failed = []
for file in sys.argv[1:]:
    if not has_module_docstring(file):
        failed.append(file)

if failed:
    print("❌ Missing module-level docstring in:")
    for f in failed:
        print("  -", f)
    sys.exit(1)
