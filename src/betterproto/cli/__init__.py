import asyncio
from pathlib import Path
from typing import Any, Dict
import os

from black import DEFAULT_LINE_LENGTH as DEFAULT_LINE_LENGTH

try:
    import grpc
except ImportError:
    USE_PROTOC = True
else:
    USE_PROTOC = False

DEFAULT_OUT = Path.cwd() / "betterproto_out"
DEFAULT_PORT = 50051
VERBOSE = False
ENV: Dict[str, Any] = dict(os.environ)
SUBPROCESS_CONNECTED = asyncio.Event()

from .commands import main

# TODO
# - env vars for options
# - remove services
# - separate files
