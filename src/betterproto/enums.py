import enum
from typing import Type, TypeVar

from .casing import camel_case, snake_case

E = TypeVar("E", bound="Enum")

__all__ = (
    "Casing",
    "Enum",
)


class Casing(enum.Enum):
    """Casing constants for serialization."""

    CAMEL = camel_case  #: A camelCase sterilization function.
    SNAKE = snake_case  #: A snake_case sterilization function.


class Enum(enum.IntEnum):
    """
    The base class for protobuf enumerations, all generated enumerations will inherit
    from this. Bases :class:`enum.IntEnum`.
    """

    @classmethod
    def from_string(cls: Type[E], name: str) -> E:
        """Return the value which corresponds to the string name.

        Parameters
        -----------
        name: :class:`str`
            The name of the enum member to get

        Raises
        -------
        :exc:`ValueError`
            The member was not found in the Enum.
        """
        try:
            return cls._member_map_[name]  # type: ignore
        except KeyError as e:
            raise ValueError(f"Unknown value {name} for enum {cls.__name__}") from e