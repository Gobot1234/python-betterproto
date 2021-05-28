import dataclasses
from typing import Any, Optional, Tuple

from betterproto.consts import *

__all__ = (
    "enum_field",
    "bool_field",
    "int32_field",
    "int64_field",
    "uint32_field",
    "uint64_field",
    "sint32_field",
    "sint64_field",
    "float_field",
    "double_field",
    "fixed32_field",
    "fixed64_field",
    "sfixed32_field",
    "sfixed64_field",
    "string_field",
    "bytes_field",
    "message_field",
    "map_field",
)


class FieldMetadata:
    """Stores internal metadata used for parsing & serialization."""
    __slots__ = ("number", "proto_type", "map_types", "group", "wraps")

    def __init__(
        self,
        number: int,
        proto_type: str,
        map_types: Optional[Tuple[str, str]] = None,
        group: Optional[str] = None,
        wraps: Optional[str] = None,
    ) -> None:
        # Protobuf field number
        self.number: int = number
        # Protobuf type name
        self.proto_type: str = proto_type
        # Map information if the proto_type is a map
        self.map_types: Optional[Tuple[str, str]] = map_types
        # Groups several "one-of" fields together
        self.group: Optional[str] = group
        # Describes the wrapped type (e.g. when using google.protobuf.BoolValue)
        self.wraps: Optional[str] = wraps

    @staticmethod
    def get(field: dataclasses.Field) -> "FieldMetadata":
        """Returns the field metadata for a dataclass field."""
        return field.metadata["betterproto"]


def dataclass_field(
    number: int,
    proto_type: str,
    *,
    map_types: Optional[Tuple[str, str]] = None,
    group: Optional[str] = None,
    wraps: Optional[str] = None,
) -> dataclasses.Field:
    """Creates a dataclass field with attached protobuf metadata."""
    return dataclasses.field(
        default=PLACEHOLDER,
        metadata={
            "betterproto": FieldMetadata(number, proto_type, map_types, group, wraps)
        },
    )


# Note: the fields below return `Any` to prevent type errors in the generated
# data classes since the types won't match with `Field` and they get swapped
# out at runtime. The generated dataclass variables are still typed correctly.


def enum_field(number: int, group: Optional[str] = None) -> Any:
    return dataclass_field(number, TYPE_ENUM, group=group)


def bool_field(number: int, group: Optional[str] = None) -> Any:
    return dataclass_field(number, TYPE_BOOL, group=group)


def int32_field(number: int, group: Optional[str] = None) -> Any:
    return dataclass_field(number, TYPE_INT32, group=group)


def int64_field(number: int, group: Optional[str] = None) -> Any:
    return dataclass_field(number, TYPE_INT64, group=group)


def uint32_field(number: int, group: Optional[str] = None) -> Any:
    return dataclass_field(number, TYPE_UINT32, group=group)


def uint64_field(number: int, group: Optional[str] = None) -> Any:
    return dataclass_field(number, TYPE_UINT64, group=group)


def sint32_field(number: int, group: Optional[str] = None) -> Any:
    return dataclass_field(number, TYPE_SINT32, group=group)


def sint64_field(number: int, group: Optional[str] = None) -> Any:
    return dataclass_field(number, TYPE_SINT64, group=group)


def float_field(number: int, group: Optional[str] = None) -> Any:
    return dataclass_field(number, TYPE_FLOAT, group=group)


def double_field(number: int, group: Optional[str] = None) -> Any:
    return dataclass_field(number, TYPE_DOUBLE, group=group)


def fixed32_field(number: int, group: Optional[str] = None) -> Any:
    return dataclass_field(number, TYPE_FIXED32, group=group)


def fixed64_field(number: int, group: Optional[str] = None) -> Any:
    return dataclass_field(number, TYPE_FIXED64, group=group)


def sfixed32_field(number: int, group: Optional[str] = None) -> Any:
    return dataclass_field(number, TYPE_SFIXED32, group=group)


def sfixed64_field(number: int, group: Optional[str] = None) -> Any:
    return dataclass_field(number, TYPE_SFIXED64, group=group)


def string_field(number: int, group: Optional[str] = None) -> Any:
    return dataclass_field(number, TYPE_STRING, group=group)


def bytes_field(number: int, group: Optional[str] = None) -> Any:
    return dataclass_field(number, TYPE_BYTES, group=group)


def message_field(
    number: int, group: Optional[str] = None, wraps: Optional[str] = None
) -> Any:
    return dataclass_field(number, TYPE_MESSAGE, group=group, wraps=wraps)


def map_field(
    number: int, key_type: str, value_type: str, group: Optional[str] = None
) -> Any:
    return dataclass_field(
        number, TYPE_MAP, map_types=(key_type, value_type), group=group
    )
