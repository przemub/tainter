"""Utils for use by program creators."""
from __future__ import annotations

from abc import abstractmethod
from typing import Callable, TypeVar

# Attribute to be set on functions always returning safe values.
_SAFE_FUNCTION_ATTRIBUTE = "__tainter_safe"

# Attribute to be set on functions which output data to the user.
# An error is to be raised when such a function gets a tainted value
# as an argument.
_OUTPUT_FUNCTION_ATTRIBUTE = "__tainter_output"

# Attribute to be set on tainted variables.
_TAINTED_VARIABLE_ATTRIBUTE = "__tainted_attribute"


class _AttributeMeta(type):
    """
    A type which considers its subclass every class that has an ATTRIBUTE.
    It adds it to its subclasses as well.
    """

    ATTRIBUTE: str | None = None

    def __instancecheck__(self, instance):
        """Instance is a subinstance iff it has the ATTRIBUTE."""
        if self.ATTRIBUTE is None:
            raise ValueError("ATTRIBUTE cannot be None!")

        return getattr(instance, self.ATTRIBUTE, None) is not None

    @classmethod
    def __subclasscheck__(cls, subclass):
        """Class is a subclass iff it has the ATTRIBUTE."""
        if cls.ATTRIBUTE is None:
            raise ValueError("ATTRIBUTE cannot be None!")

        return getattr(subclass, cls.ATTRIBUTE, None) is not None

    def __init__(self, *args, **kwargs):
        if self.ATTRIBUTE is None:
            raise ValueError("ATTRIBUTE cannot be None!")

        super().__init__(*args, **kwargs)
        setattr(self, self.ATTRIBUTE, True)


class _SafeMeta(_AttributeMeta):
    """
    A metaclass which instead of using normal subclassing semantics,
    simply checks if _SAFE_ATTRIBUTE is declared.
    By declaring _SAFE_ATTRIBUTE you tell the tainter that this method
    processes its input safely.

    See: mark_safe.
    """
    ATTRIBUTE = _SAFE_FUNCTION_ATTRIBUTE


class Safe(metaclass=_SafeMeta):
    """
    A value returned when this class sub-instance is called
    is untainted even if a tainted variable is passed to it.
    """

    @abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError()


# Some functions should be considered output by default.
OUTPUT_FUNCTIONS = [
    "print",
    "sys.write"
]


class _OutputMeta(_AttributeMeta):
    """
    A metaclass which instead of using normal subclassing semantics,
    simply checks if _OUTPUT_ATTRIBUTE is declared on the instance.
    By declaring _OUTPUT_ATTRIBUTE you tell the tainter that passing
    a tainted value to the instance is a bad thing.

    There are also some built-in functions which we mark as outputs -
    print, for example.

    See: mark_output.
    """

    ATTRIBUTE = _OUTPUT_FUNCTION_ATTRIBUTE


class Output(metaclass=_OutputMeta):
    """
    When this class sub-instance is called with a tainted variable,
    we have a leak.
    """

    @abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError()


T = TypeVar("T", bound=Callable)


def mark_safe(func: T) -> T:
    """
    This decorator marks a callable as "safe".
    You can check that a callable is safe at run-time by:
    1) checking if the callable is an instance of Safe (isinstance(func, Safe))
    2) using is_safe(), which does the above
    3) checking for the SAFE_ATTRIBUTE (not recommended, since the semantics may
       change.
    """

    setattr(func, _SAFE_FUNCTION_ATTRIBUTE, True)
    return func


def is_safe(func: Callable) -> bool:
    return isinstance(func, Safe)


def mark_output(func: T) -> T:
    """
    This decorator marks a callable as an output function.
    """

    setattr(func, _OUTPUT_FUNCTION_ATTRIBUTE, True)
    return func


def mark_tainted(value=None):
    return value
    # TODO: Find a way to check taintedness at runtime.
