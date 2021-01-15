import asyncio
from dataclasses import dataclass
from typing import AsyncIterator

import betterproto
import grpclib


class CurrentlyCompilingType(betterproto.Enum):
    ENUM = 0
    MESSAGE = 1
    SERVICE = 2


@dataclass
class CurrentlyCompiling(betterproto.Message):
    name: str = betterproto.string_field(1)
    type: CurrentlyCompilingType = betterproto.enum_field(2)


# TODO needs client and server classes
