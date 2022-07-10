"""Utils for use by program creators."""
from abc import abstractmethod
from typing import Callable, TypeVar

# Attribute to be set on safe functions.
_SAFE_ATTRIBUTE = "__tainter_safe"


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


class Safe(metaclass=_SafeMeta):
    """
    A value returned when this class sub-instance is called
    is untainted even if a tainted variable is passed to it.
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
