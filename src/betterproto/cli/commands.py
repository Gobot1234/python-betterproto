import asyncio
import sys
from pathlib import Path

import click
import rich
from grpclib.client import Channel
from rich.progress import Progress

from . import VERBOSE, USE_PROTOC, DEFAULT_OUT, ENV, connected_to_subprocess, DEFAULT_PORT
from .services import CurrentlyCompiling
from .utils import recursive_file_finder, compile_files


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
    "-l",
    "--line-length",
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
    "--port",
    help="The output directory",
    type=int,
    default=DEFAULT_PORT,
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
def compile(verbose: bool, protoc: bool, generate_services: bool, port: int, output: str, src: str) -> None:
    """The recommended way to compile your protobuf files."""

    directory = (Path.cwd() / src).resolve()
    files = recursive_file_finder(directory) if directory.is_dir() else (directory,)
    if not files:
        return rich.print("[bold]No files found to compile")

    output = Path.cwd() / output
    output.mkdir(exist_ok=True)

    ENV["VERBOSE"] = str(int(verbose))
    ENV["GENERATE_SERVICES"] = str(int(generate_services))
    ENV["USE_PROTOC"] = str(int(protoc and USE_PROTOC))

    async def runner() -> None:
        loop = asyncio.get_event_loop()
        connected_to_subprocess._loop = loop  # make sure we don't run into issues using different loops due to asyncio.run
        await run_cli(port)
        stdout, stderr, return_code = await compile_files(*files, output_dir=output)

        if return_code != 0:
            failed_files = "\n".join(f" - {file}" for file in files)
            return rich.print(
                f"[red]{'Protoc' if ENV['USE_PROTOC'] else 'GRPC'} failed to generate outputs for:\n\n"
                f"{failed_files}\n\nSee the output for the issue:\n{stderr}", file=sys.stderr
            )

        rich.print(f"[bold]Finished generating output for {len(files)} files, compiled output should be in {output.as_posix()}")

    try:
        asyncio.run(runner())
    except AttributeError:  # py 3.6
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(runner())
        finally:
            loop.close()


async def run_cli(port: int) -> None:
    await connected_to_subprocess.wait()

    async with Channel(port=port) as channel:
        service = Stub(channel)
        total: int = await service.request_total_messages()
        with Progress(transient=True) as progress:
            compiling_progress_bar = progress.add_task("[green]Compiling protobufs...", total=total)

            async for message in service.request_currently_compiling():
                message: CurrentlyCompiling
                progress.tasks[0].description = f"[green]Compiling protobufs...\n" \
                                                f"Currently compiling {message.type.name.lower()}: {message.name}"
                progress.update(compiling_progress_bar, advance=1)
        rich.print(f"[bold][green]Finished compiling output should be at {round(3)}")
