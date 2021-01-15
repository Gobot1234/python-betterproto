#!/usr/bin/env python
import asyncio
import os
from pathlib import Path
import platform
import sys
from typing import Set

import click

from tests.util import (
    get_directories,
    inputs_path,
    output_path_betterproto,
    output_path_reference,
)
from betterproto.cli import compile_files

# Force pure-python implementation instead of C++, otherwise imports
# break things because we can't properly reset the symbol database.
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"


def clear_directory(dir_path: Path):
    for file_or_directory in dir_path.glob("*"):
        file_or_directory.rmdir() if file_or_directory.is_dir() else file_or_directory.unlink()


async def generate(whitelist: Set[str], verbose: bool):
    test_case_names = set(get_directories(inputs_path)) - {"__pycache__"}

    path_whitelist = set()
    name_whitelist = set()
    for item in whitelist:
        if item in test_case_names:
            name_whitelist.add(item)
            continue
        path_whitelist.add(item)

    generation_tasks = []
    for test_case_name in sorted(test_case_names):
        test_case_input_path = inputs_path.joinpath(test_case_name).resolve()
        if (
            whitelist
            and str(test_case_input_path) not in path_whitelist
            and test_case_name not in name_whitelist
        ):
            continue
        generation_tasks.append(
            generate_test_case_output(test_case_input_path, test_case_name, verbose)
        )

    failed_test_cases = []
    # Wait for all subprocs and match any failures to names to report
    for test_case_name, result in zip(
        sorted(test_case_names), await asyncio.gather(*generation_tasks)
    ):
        if result != 0:
            failed_test_cases.append(test_case_name)

    if failed_test_cases:
        sys.stderr.write(
            "\n\033[31;1;4mFailed to generate the following test cases:\033[0m\n"
        )
        for failed_test_case in failed_test_cases:
            sys.stderr.write(f"- {failed_test_case}\n")


async def generate_test_case_output(
    test_case_input_path: Path, test_case_name: str, verbose: bool
) -> int:
    """
    Returns the max of the subprocess return values
    """

    test_case_output_path_reference = output_path_reference.joinpath(test_case_name)
    test_case_output_path_betterproto = output_path_betterproto.joinpath(test_case_name)

    os.makedirs(test_case_output_path_reference, exist_ok=True)
    os.makedirs(test_case_output_path_betterproto, exist_ok=True)

    clear_directory(test_case_output_path_reference)
    clear_directory(test_case_output_path_betterproto)

    (
        (ref_out, ref_err, ref_code),
        (plg_out, plg_err, plg_code),
    ) = await asyncio.gather(
        compile_files(test_case_input_path, test_case_output_path_reference, ""),
        compile_files(test_case_input_path, test_case_output_path_betterproto),
    )

    message = f"Generated output for {test_case_name!r}"
    if verbose:
        print(f"\033[31;1;4m{message}\033[0m")
        if ref_out:
            sys.stdout.buffer.write(ref_out)
        if ref_err:
            sys.stderr.buffer.write(ref_err)
        if plg_out:
            sys.stdout.buffer.write(plg_out)
        if plg_err:
            sys.stderr.buffer.write(plg_err)
        sys.stdout.buffer.flush()
        sys.stderr.buffer.flush()
    else:
        print(message)

    return max(ref_code, plg_code)


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    default=False,
)
@click.option("src", nargs=-1)
def main(verbose: bool, src: str):
    print(src)
    if platform.system() == "Windows":
        asyncio.set_event_loop(asyncio.ProactorEventLoop())

    asyncio.get_event_loop().run_until_complete(generate(src, verbose))


if __name__ == "__main__":
    sys.argv = "-v lol .lolo text".split()
    main()
