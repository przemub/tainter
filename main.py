from __future__ import annotations

import argparse
import ast
import logging
import sys
from _ast import FunctionDef, Return, Name, Assign, Call
from functools import cached_property
from textwrap import indent
from typing import TypeVar, Container, Iterable
from warnings import warn

from termcolor import colored

T = TypeVar("T", bound=ast.AST)

logger = logging.getLogger(__name__)


def find_subnodes(tree: ast.AST, classes: Iterable[type[T]],
                  **kwargs: Container) -> list[T]:
    """
    Recursively finds nodes node in a tree of given classes and with
    matching kwargs.

    For example, find_submodule(tree, [Name], id=["a"]) will find a variable named
    "a", while find_submodule(tree, [Name], id=["a", "b"]) will find variables
    named either a or b.
    """
    items = []
    for item in ast.walk(tree):
        if isinstance(item, tuple(classes)) and all(
            getattr(item, key, None) in values for key, values in
            kwargs.items()
        ):
            items.append(item)

    return items


def find_subnode(tree: ast.AST, klass: type[T], **kwargs) -> T:
    subnodes = find_subnodes(tree, [klass],
                             **{key: [val] for key, val in kwargs.items()})
    if len(subnodes) == 0:
        raise ValueError("There is no such subnode.")
    elif len(subnodes) == 1:
        return subnodes[0]
    else:
        raise ValueError("There exists more than one such subnode!")


def load_file(filename: str) -> tuple[str, ast.AST]:
    """
    Load file and return its contents and AST parsed from
    the contents.
    """
    with open(filename) as file:
        data = file.read()

    return data, ast.parse(data, filename)


class TaintVisitor(ast.NodeVisitor):
    def _warn_tainted(self, node, tab=0):
        message = ""

        if node.lineno == node.end_lineno:
            message += f"Line {node.lineno} tainted:\n"
        else:
            message += f"Lines {node.lineno}-{node.end_lineno} tainted:\n"

        # Print the whole tainted line and underline the problem
        underline_start, underline_end = node.col_offset, node.end_col_offset
        node.col_offset = 0
        node.end_col_offset = -1
        message += ast.get_source_segment(self._source, node) + "\n"

        underline = ""
        counter = 0
        while counter < underline_start:
            counter += 1
            underline += " "
        while counter < underline_end:
            counter += 1
            underline += "^"
        message += colored(underline, "red")

        tainted_variables = find_subnodes(
            node, (Name,), id=self.tainted_variables
        )

        prefix = "->" * tab + " "
        output = indent(message, prefix, lambda _: tab > 0)
        self.output += output
        print(output)

        tab += 1
        for variable in tainted_variables:
            reason = self._tainted_because[variable.id]
            if reason is node:
                continue

            self._warn_tainted(
                reason, tab
            )

    def __init__(self, tree: ast.AST, tainted_because: dict[str, ast.AST], source: str):
        self._source = source
        self._tainted_because = tainted_because
        self._tainted_nodes: list[ast.AST] = []

        # Preserve output for further analysis.
        self.output = ""

        self.tree = tree
        self.visit(tree)

    @cached_property
    def safe_functions(self) -> list[str]:
        """Collect and return the list of functions marked with mark_safe."""
        # TODO: Collect also the imported functions.
        # TODO: Collect functions marked without the @ decorator syntax.
        #       This will be useful for marking imported functions.

        results = []

        tree = ast.parse(self._source)
        functions = find_subnodes(tree, [FunctionDef])
        for function in functions:
            for decorator in function.decorator_list:
                if not isinstance(decorator, Name):
                    continue
                if decorator.id == "mark_safe":
                    results.append(function.name)

        return results

    @property
    def tainted_variables(self):
        return self._tainted_because.keys()

    @property
    def tainted_nodes(self):
        return self._tainted_nodes

    def visit_Name(self, node: Name):
        if node.id in self.tainted_variables:
            self._tainted_nodes.append(node)

    def visit_Assign(self, node: Assign):
        visitor = TaintVisitor(node.value, self._tainted_because, self._source)

        if visitor.tainted_nodes:
            for variable in node.targets:
                if not isinstance(variable, Name):
                    continue

                self._tainted_because[variable.id] = node

    def visit_Call(self, node: Call):
        """
        If the function call was determined safe, don't go down.
        If the function call was determined an output, shout when a tainted
        variable is used.
        Otherwise, continue as usual.
        """

        if not isinstance(node.func, Name):
            warn(f"Calls to non-named functions not yet supported. Line: {node.lineno}")
            return
        if node.func.id in self.safe_functions:
            return
        #if node.func.id in self.output_functions:
        # pass

        return super().generic_visit(node)


    def visit_Return(self, node: Return):
        """
        We want to warn when returning a tainted variable, therefore
        we check if the return value includes anything tainted.
        """
        if node.value is None:
            return

        visitor = TaintVisitor(node.value, self._tainted_because, self._source)

        if visitor.tainted_nodes:
            for item in visitor.tainted_nodes:
                self._tainted_nodes += [node]
                self._warn_tainted(node)


def taint(function: FunctionDef, argument: str, source):
    for arg in function.args.args:
        if arg.arg == argument:
            visitor = TaintVisitor(function, {argument: arg}, source)
            return visitor

    raise ValueError("The given argument does not exist in this function.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Tainting tracker.')
    parser.add_argument("filename")
    parser.add_argument("function")
    parser.add_argument("-d", "--dump", action="store_true")
    parser.add_argument("-t", "--taint", action="extend", nargs="+")
    args = parser.parse_args()

    source, my_ast = load_file(args.filename)
    functions = find_subnodes(my_ast, (FunctionDef,), name=[args.function])

    if not functions:
        print("This function does not exist in the file!")
        sys.exit(1)
    elif len(functions) > 1:
        print("There is more than one such function?")
        sys.exit(2)

    function = functions[0]

    if args.dump:
        print(ast.dump(function, indent=2))

    for argument in args.taint or []:
        taint(function, argument, source)
