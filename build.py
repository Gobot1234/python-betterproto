import shutil
import subprocess
from pathlib import Path

BETTERPROTO = Path("src", "betterproto")


try:
    import mypyc  # type: ignore[import]
except ImportError:
    pass
else:
    process = subprocess.run(
        [
            "mypyc",
            *(
                f
                for f in BETTERPROTO.iterdir()
                if f.name not in ("__init__.py", "__main__.py") and f.suffix == ".py"
            ),
        ]
    )
    if process.returncode != 0:
        raise RuntimeError("Cannot compile extensions")
    shutil.rmtree("build", ignore_errors=True)
    # shutil.move(
    #     [f for f in Path().parent.iterdir() if "mypyc" in f.name and f.suffix == ".so"][
    #         0
    #     ],
    #     "src",
    # )
    # shutil.move(Path("betterproto"), "src")
