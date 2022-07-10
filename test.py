from _ast import FunctionDef, Return
from unittest import TestCase

from main import load_file, find_subnode, taint, TaintVisitor
from utils import is_safe, mark_safe


def taint_argument(file, function_name, tainted_arg="a"):
    """
    Have a test unit load a Python file, find a function in it,
    taint the argument, run the tainter and make sure that
    the returned value was tainted.
    """

    def decorator(test_unit):
        source, ast = load_file("examples/" + file)
        function = find_subnode(
            ast, FunctionDef, name=function_name
        )
        tainter = taint(
            function, tainted_arg, source
        )

        def call(self: "TainterTestCase"):
            test_unit(self, tainter)
            self.assertTaintedReturn(tainter)

        return call

    return decorator


class TainterTestCase(TestCase):
    def assertTaintedReturn(self, tainter: TaintVisitor):
        tainted_return = find_subnode(tainter.tree, Return)
        self.assertIn(
            tainted_return,
            tainter.tainted_nodes,
            msg="The return was not tainted as expected.",
        )

    def assertInOutput(self, text: str, tainter: TaintVisitor):
        self.assertIn(
            text, tainter.output, msg=f"{text} was not found in the output."
        )

    @taint_argument("return_argument.py", "simple")
    def test_simple(self, tainter):
        self.assertInOutput("return a", tainter)
        self.assertInOutput("-> def simple(a)", tainter)

    @taint_argument("return_argument.py", "with_op")
    def test_with_op(self, tainter):
        self.assertInOutput("return a + 5", tainter)
        self.assertInOutput("-> def with_op(a)", tainter)

    @taint_argument("return_argument.py", "with_call")
    def test_with_call(self, tainter):
        self.assertInOutput("return math.pow(a, 2)", tainter)
        self.assertInOutput("-> def with_call(a)", tainter)

    @taint_argument("assignment.py", "reassign")
    def test_reassign(self, tainter):
        self.assertInOutput("return b", tainter)
        self.assertInOutput("b = a", tainter)
        self.assertInOutput("->-> reassign(a)", tainter)

    @taint_argument("assignment.py", "chain")
    def test_chain(self, tainter):
        self.assertInOutput("return e", tainter)
        self.assertInOutput("e = d", tainter)
        self.assertInOutput("d = c", tainter)
        self.assertInOutput("c = a", tainter)
        self.assertInOutput("->->->-> def chain(a):", tainter)
        pass


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
