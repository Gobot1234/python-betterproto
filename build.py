import shutil
from distutils.command.build_ext import build_ext  # type: ignore[import]
from distutils.dist import Distribution
from pathlib import Path
from typing import Any, Dict, cast

from tomlkit import parse

BETTERPROTO = Path("src", "betterproto")

PYPROJECT = cast(Dict[str, Any], parse(Path("pyproject.toml").read_text()))
VERSION: str = PYPROJECT["tool"]["poetry"]["version"]

BETTERPROTO.joinpath("_version.py").write_text(
    f'__version__ = "{VERSION}"\n'
)  # has to be done before compilation for import to be resolved

try:
    from mypyc import build  # type: ignore[import]
except ImportError:
    pass
else:
    command = build_ext(Distribution())
    command.finalize_options()
    command.build_lib = str(BETTERPROTO.parent)
    try:
        command.extensions = build.mypycify(
            [str(p) for p in sorted(BETTERPROTO.glob("*.py"))],
        )
        command.run()
    except Exception:
        pass
    else:
        shutil.rmtree("build", ignore_errors=True)
