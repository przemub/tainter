from _ast import FunctionDef, Return
from unittest import TestCase

from main import load_file, find_subnode, taint
from utils import is_safe, mark_safe


class TainterTestCase(TestCase):
    def test_simple(self):
        source, my_ast = load_file("examples/return_argument.py")
        function = find_subnode(my_ast, FunctionDef, name="simple")
        tainter = taint(function, "a", source)

        tainted_return = find_subnode(function, Return)
        self.assertIn(tainted_return, tainter.tainted_nodes)

    def test_with_op(self):
        source, my_ast = load_file("examples/return_argument.py")
        function = find_subnode(my_ast, FunctionDef, name="with_op")
        tainter = taint(function, "a", source)

        tainted_return = find_subnode(function, Return)
        self.assertIn(tainted_return, tainter.tainted_nodes)


    def test_with_call(self):
        source, my_ast = load_file("examples/return_argument.py")
        function = find_subnode(my_ast, FunctionDef, name="with_call")
        tainter = taint(function, "a", source)

        tainted_return = find_subnode(function, Return)
        self.assertIn(tainted_return, tainter.tainted_nodes)


    def test_reassign(self):
        source, my_ast = load_file("examples/assignment.py")
        function = find_subnode(my_ast, FunctionDef, name="reassign")
        tainter = taint(function, "a", source)

        tainted_return = find_subnode(function, Return)
        self.assertIn(tainted_return, tainter.tainted_nodes)

    def test_chain(self):
        source, my_ast = load_file("examples/assignment.py")
        function = find_subnode(my_ast, FunctionDef, name="chain")
        tainter = taint(function, "a", source)

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
