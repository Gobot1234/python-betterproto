import asyncio
from pathlib import Path
from typing import Any, Dict

try:
    import grpc
except ImportError:
    USE_PROTOC = True
else:
    USE_PROTOC = False

DEFAULT_OUT = Path.cwd() / "betterproto_out"
DEFAULT_PORT = 50051
VERBOSE = False
ENV: Dict[str, Any] = {}
connected_to_subprocess = asyncio.Event()

from .commands import main

# TODO
# - env vars for options
# - remove services
# - separate files
