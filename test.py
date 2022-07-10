from __future__ import annotations

from _ast import FunctionDef, Return
from unittest import TestCase, expectedFailure

from main import load_file, find_subnode, taint, TaintVisitor
from utils import is_safe, mark_safe


def taint_argument(
    file, function_name, tainted_arg="a", tainted: bool | None = True
):
    """
    Have a test unit load a Python file, find a function in it,
    taint the argument, run the tainter and make sure that
    the returned value was tainted if tainted=True.
    """

    def decorator(test_unit):
        def call(self: "TainterTestCase"):
            source, ast = load_file("examples/" + file)
            function = find_subnode(ast, FunctionDef, name=function_name)
            tainter = taint(function, tainted_arg, source)

            test_unit(self, tainter)
            if tainted is True:
                self.assertTainted(function_name, tainter)
            elif tainted is False:
                self.assertNotTainted(function_name, tainter)
            else:
                pass

        return call

    return decorator


class TainterTestCase(TestCase):
    def assertTainted(self, func: str, tainter: TaintVisitor):
        self.assertInOutput(f"def {func}", tainter)

    def assertNotTainted(self, func: str, tainter: TaintVisitor):
        self.assertNotInOutput(f"def {func}", tainter)

    def assertInOutput(self, text: str, tainter: TaintVisitor):
        self.assertIn(
            text, tainter.output, msg=f"{text} was not found in the output."
        )

    def assertNotInOutput(self, text: str, tainter: TaintVisitor):
        self.assertNotIn(
            text, tainter.output, msg=f"{text} was found in the output."
        )

    @taint_argument("return_argument.py", "simple")
    def test_simple(self, tainter):
        self.assertInOutput("return a", tainter)
        self.assertInOutput("-> def simple(a)", tainter)

    @taint_argument("return_argument.py", "with_op")
    def test_with_op(self, tainter):
        self.assertInOutput("return a + 5", tainter)
        self.assertInOutput("-> def with_op(a)", tainter)

    @expectedFailure  # TODO
    @taint_argument("return_argument.py", "with_call")
    def test_with_call(self, tainter):
        self.assertInOutput("return math.pow(a, 2)", tainter)
        self.assertInOutput("-> def with_call(a)", tainter)

    @taint_argument("return_argument.py", "with_direct_call")
    def test_with_call(self, tainter):
        self.assertInOutput("return _b(a)", tainter)
        self.assertInOutput("-> def with_direct_call(a)", tainter)

    @taint_argument("assignment.py", "reassign")
    def test_reassign(self, tainter):
        self.assertInOutput("return b", tainter)
        self.assertInOutput("b = a", tainter)
        self.assertInOutput("->-> def reassign(a)", tainter)

    @taint_argument("assignment.py", "chain")
    def test_chain(self, tainter):
        self.assertInOutput("return e", tainter)
        self.assertInOutput("e = d", tainter)
        self.assertInOutput("d = c", tainter)
        self.assertInOutput("c = a", tainter)
        self.assertInOutput("->->->-> def chain(a):", tainter)
        pass

    @taint_argument("call.py", "safe_call", tainted=False)
    def test_safe_call(self, tainter):
        pass

    @taint_argument("call.py", "unsafe_call")
    def test_unsafe_call(self, tainter):
        pass

    @taint_argument("call.py", "print_test")
    def test_print(self, tainter):
        pass

    @taint_argument("call.py", "mark_output_test")
    def test_mark_output(self, tainter):
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
