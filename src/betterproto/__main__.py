import subprocess
import sys
from functools import partial
from pathlib import Path
from typing import Any, Dict, Tuple

try:
    import black
    import click
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

try:
    import grpc
except ImportError:
    USE_PROTOC = True
else:
    USE_PROTOC = False

DEFAULT_OUT = Path.cwd() / "betterproto_out"
VERBOSE = False
ENV: Dict[str, Any] = {}

out = partial(click.secho, bold=True, err=True)
err = partial(click.secho, fg="red", err=True)


def recursive_file_finder(directory: Path) -> Tuple[Path, ...]:
    files = set()
    for path in directory.iterdir():
        if path.is_file() and path.name.endswith(".proto"):
            files.add(path)
        elif path.is_dir():
            files.update(recursive_file_finder(path))

    return tuple(files)


def compile_files(*files: Path, output_dir: Path) -> None:
    cwd = files[0].parent.resolve().as_posix()
    files = [file.relative_to(cwd).as_posix() for file in files]
    command = [
        f"--python_betterproto_out={output_dir.as_posix()}",
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

    proc = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV, cwd=cwd
    )
    stdout, stderr = proc.communicate()
    stdout = stdout.decode()
    stderr = stderr.decode()

    if proc.returncode != 0:
        failed_files = "\n".join(f" - {file}" for file in files)
        return err(
            f"{'Protoc' if ENV['USE_PROTOC'] else 'GRPC'} failed to generate outputs for:\n\n"
            f"{failed_files}\n\nSee the output for the issue:\n{stderr}"
        )

    if ENV["VERBOSE"]:
        out(f"VERBOSE: {stdout}")

    out(f"Finished generating output for {len(files)} files, compiled output should be in {output_dir.as_posix()}")


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.pass_context
def main(ctx: click.Context):
    """The main entry point to all things betterproto"""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    default=VERBOSE,
)
@click.option(
    "-p",
    "--protoc",
    is_flag=True,
    help="Whether or not to use protoc to compile the protobufs if this is false it will attempt to use grpc instead",
    default=USE_PROTOC,
)
@click.option(
    "--generate-services",
    help="Whether or not to generate servicer stubs",
    is_flag=True,
    default=True,
)
@click.option(
    "-o",
    "--output",
    help="The output directory",
    type=click.Path(
        file_okay=False, dir_okay=True, allow_dash=True
    ),
    default=DEFAULT_OUT.name,
    is_eager=True,
)
@click.argument(
    "src",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=True, allow_dash=True
    ),
    is_eager=True,
)
def compile(verbose: bool, protoc: bool, generate_services: bool, output: str, src: str) -> None:
    """The recommended way to compile your protobuf files."""

    directory = (Path.cwd() / src).resolve()
    files = recursive_file_finder(directory) if directory.is_dir() else (directory,)
    if not files:
        return out("No files found to compile")

    output = Path.cwd() / output
    output.mkdir(exist_ok=True)

    ENV["VERBOSE"] = str(int(verbose))
    ENV["GENERATE_SERVICES"] = str(int(generate_services))
    ENV["USE_PROTOC"] = str(int(protoc and USE_PROTOC))

    return compile_files(*files, output_dir=output)


if __name__ == "__main__":
    black.patch_click()
    # sys.argv = "betterproto compile ../../tests/inputs/service".split()
    main()


# TODO
# - env vars for options
# - remove services
# - separate files
