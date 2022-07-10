"""Utils for use by program creators."""
from abc import abstractmethod
from typing import Callable, TypeVar

# Attribute to be set on functions always returning safe values.
_SAFE_ATTRIBUTE = "__tainter_safe"

# Attribute to be set on functions which output data to the user.
# An error is to be raised when such a function gets a tainted value
# as an argument.
_OUTPUT_ATTRIBUTE = "__tainter_output"


class _SafeMeta(type):
    """
    A metaclass which instead of using normal subclassing semantics,
    simply checks if _SAFE_ATTRIBUTE is declared.
    By declaring _SAFE_ATTRIBUTE you tell the tainter that this method
    processes its input safely.

    See: mark_safe.
    """

    def __instancecheck__(self, instance):
        """Instance is a subinstance iff it has _SAFE_ATTRIBUTE."""
        return getattr(instance, _SAFE_ATTRIBUTE, None) is not None

    @classmethod
    def __subclasscheck__(cls, subclass):
        """Class is a subclass iff it has _SAFE_ATTRIBUTE."""
        return getattr(subclass, _SAFE_ATTRIBUTE, None) is not None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        setattr(self, _SAFE_ATTRIBUTE, True)


class Safe(metaclass=_SafeMeta):
    """
    A value returned when this class sub-instance is called
    is untainted even if a tainted variable is passed to it.
    """

    @abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError()


class _OutputMeta(type):
    """
    A metaclass which instead of using normal subclassing semantics,
    simply checks if _OUTPUT_ATTRIBUTE is declared on the instance.
    By declaring _OUTPUT_ATTRIBUTE you tell the tainter that passing
    a tainted value to the instance is a bad thing.

    There are also some built-in functions which we mark as outputs -
    print, for example.

    See: mark_output.
    """

    def __instancecheck__(self, instance):
        """Instance is a subinstance iff it has _SAFE_ATTRIBUTE."""
        return getattr(instance, _OUTPUT_ATTRIBUTE, None) is not None

    @classmethod
    def __subclasscheck__(cls, subclass):
        """Class is a subclass iff it has _SAFE_ATTRIBUTE."""
        return getattr(subclass, _OUTPUT_ATTRIBUTE, None) is not None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        setattr(self, _SAFE_ATTRIBUTE, True)


class Output(metaclass=_SafeMeta):
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
    You can check that a callable is safe by:
    1) checking if the callable is an instance of Safe (isinstance(func, Safe))
    2) using is_safe(), which does the above
    3) checking for the SAFE_ATTRIBUTE (unrecommended, since the semantics may
       change.
    """

    setattr(func, _SAFE_ATTRIBUTE, True)
    return func


def is_safe(func: Callable) -> bool:
    return isinstance(func, Safe)


def mark_output(func: T) -> T:
    """
    This decorator marks a callable as an output function.
    """

    setattr(func, _OUTPUT_ATTRIBUTE, True)
    return func
