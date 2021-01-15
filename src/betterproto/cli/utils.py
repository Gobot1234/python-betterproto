import asyncio
import sys
from pathlib import Path
from typing import Tuple, Optional

from src.betterproto.cli import connected_to_subprocess, ENV

try:
    import black
    import click
    from rich.progress import track, Progress
except ImportError as err:
    print(
        "\033[31m"
        f"Unable to import `{err.name}` from betterproto plugin! "
        "Please ensure that you've installed betterproto as "
        '`pip install "betterproto[compiler]"` so that compiler dependencies '
        "are included."
        "\033[0m"
    )
    raise SystemExit(1)


def recursive_file_finder(directory: Path) -> Tuple[Path, ...]:
    files = set()
    for path in directory.iterdir():
        if path.is_file() and path.name.endswith(".proto"):
            files.add(path)
        elif path.is_dir():
            files.update(recursive_file_finder(path))

    return tuple(files)


async def compile_files(
    *files: Path, output_dir: Path, implementation: str = "betterproto_"
) -> Tuple[str, str, Optional[int]]:
    cwd = files[0].parent.resolve().as_posix()
    files = [file.relative_to(cwd).as_posix() for file in files]
    command = [
        f"--python_{implementation}out={output_dir.as_posix()}",
        "-I",
        cwd,
        *files,
    ]
    if ENV["USE_PROTOC"]:
        command.insert(0, "/Users/gobot1234/Downloads/protoc")
    else:
        command.insert(0, "grpc.tools.protoc")
        command.insert(0, "-m")
        command.insert(0, sys.executable)

    proc = await asyncio.create_subprocess_shell(
        " ".join(command), stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, env=ENV, cwd=cwd
    )
    connected_to_subprocess.set()
    stdout, stderr = await proc.communicate()
    return stdout.decode(), stderr.decode(), proc.returncode

