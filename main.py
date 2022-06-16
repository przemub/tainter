from __future__ import annotations

import argparse
import ast
import sys
from _ast import FunctionDef, stmt, Return, Name
from typing import TypeVar

T = TypeVar("T", bound=stmt)


def find_subnode(tree: ast.AST, klass: type[T], **kwargs) -> T | None:
    """
    Recursively finds a node in a tree of a given class and with
    matching kwargs.

    For example, find_submodule(tree, Name, id="a") will find a variable named
    "a".
    """
    for item in ast.walk(tree):
        if isinstance(item, klass) and all(
                getattr(item, key, None) == value for key, value in
                kwargs.items()
        ):
            return item

    return None


def load_file(filename: str) -> tuple[str, ast.AST]:
    with open(filename) as file:
        data = file.read()

    return data, ast.parse(data, filename)


class TaintVisitor(ast.NodeVisitor):
    def _warn_tainted(self, node, subnode):
        print(f"Line {node.lineno} tainted:")

        print(ast.get_source_segment(self.source, node, padded=True))
        print("-> ", end="")
        print(ast.get_source_segment(self.source, subnode, padded=True))

        print()

    def __init__(self, tainted_variables: set, source: str):
        self.tainted_variables = tainted_variables
        self.source = source
        self._tainted_nodes: list[ast.AST] = []

    @property
    def tainted_nodes(self):
        return self._tainted_nodes

    def visit_Name(self, node: Name):
        if node.id in self.tainted_variables:
            self._tainted_nodes.append(node)

    def visit_Return(self, node: Return):
        """
        We want to warn when returning a tainted variable, therefore
        we check if the return value includes anything tainted.
        """
        if node.value is None:
            return

        visitor = TaintVisitor(self.tainted_variables, self.source)
        visitor.visit(node.value)

        if visitor.tainted_nodes:
            self._tainted_nodes += [node]

            for item in visitor.tainted_nodes:
                self._warn_tainted(node, item)


def taint(function: FunctionDef, argument: str, source):
    if not (argument in (arg.arg for arg in function.args.args)):
        raise ValueError("The given argument does not exist in this function.")

    visitor = TaintVisitor(argument, source)
    visitor.visit(function)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Tainting tracker.')
    parser.add_argument("filename")
    parser.add_argument("function")
    parser.add_argument("-d", "--dump", action="store_true")
    parser.add_argument("-t", "--taint", action="extend", nargs="+")
    args = parser.parse_args()

    source, my_ast = load_file(args.filename)
    function = find_subnode(my_ast, FunctionDef, name=args.function)

    if function is None:
        print("This function does not exist in the file!")
        sys.exit(1)

    if args.dump:
        print(ast.dump(function, indent=2))

    for argument in args.taint or []:
        taint(function, argument, source)
