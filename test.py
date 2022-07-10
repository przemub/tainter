from _ast import FunctionDef, Return
from unittest import TestCase

from main import load_file, find_subnode, TaintVisitor
from utils import is_safe, mark_safe


class TainterTestCase(TestCase):
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


    def test_with_call(self):
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

    def test_chain(self):
        source, my_ast = load_file("examples/assignment.py")
        function = find_subnode(my_ast, FunctionDef, name="chain")
        tainter = TaintVisitor({"a"}, source)
        tainter.visit(function)

        tainted_return = find_subnode(function, Return)
        self.assertIn(tainted_return, tainter.tainted_nodes)


class MarkSafeTestCase(TestCase):
    def test_mark_safe(self):
        def a():
            pass

        self.assertFalse(is_safe(a))

        mark_safe(a)
        self.assertTrue(is_safe(a))

    def test_decorator(self):
        @mark_safe
        def a():
            pass

        self.assertTrue(is_safe(a))
