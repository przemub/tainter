from _ast import FunctionDef, Return
from unittest import TestCase

from main import load_file, find_subnode, TaintVisitor


class TainerTestCase(TestCase):
    def test_simple(self):
        source, my_ast = load_file("examples/return_argument.py")
        function = find_subnode(my_ast, FunctionDef, name="simple")
        tainter = TaintVisitor({"a"}, source)
        tainter.visit(function)

        tainted_return = find_subnode(function, Return)
        self.assertIn(tainted_return, tainter.tainted_nodes)

    def test_with_op(self):
        source, my_ast = load_file("examples/return_argument.py")
        function = find_subnode(my_ast, FunctionDef, name="with_op")
        tainter = TaintVisitor({"a"}, source)
        tainter.visit(function)

        tainted_return = find_subnode(function, Return)
        self.assertIn(tainted_return, tainter.tainted_nodes)


    def test_with_op(self):
        source, my_ast = load_file("examples/return_argument.py")
        function = find_subnode(my_ast, FunctionDef, name="with_call")
        tainter = TaintVisitor({"a"}, source)
        tainter.visit(function)

        tainted_return = find_subnode(function, Return)
        self.assertIn(tainted_return, tainter.tainted_nodes)


    def test_reassign(self):
        source, my_ast = load_file("examples/assignment.py")
        function = find_subnode(my_ast, FunctionDef, name="reassign")
        tainter = TaintVisitor({"a"}, source)
        tainter.visit(function)

        tainted_return = find_subnode(function, Return)
        self.assertIn(tainted_return, tainter.tainted_nodes)
