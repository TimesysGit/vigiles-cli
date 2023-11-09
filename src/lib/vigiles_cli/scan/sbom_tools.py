# SPDX-FileCopyrightText: 2023 Timesys Corporation
# SPDX-License-Identifier: MIT

import datetime
import os.path
import subprocess
import sys
from .utils import err, warn, print_tool


class SbomTool(object):
    pass


class Syft(SbomTool):
    @staticmethod
    def get_sbom_path(tool_args):
        if "--output" not in tool_args and "-o" not in tool_args:
            raise Exception("Could not identify sbom marker in the argument.")
        return tool_args.split("-o")[-1].split("=")[-1].split(" ")[0].strip()

    @staticmethod
    def get_run_args(source, sbom_name):
        sbom_file = (
            sbom_name + ".json"
            if sbom_name
            else "cyclonedx-%s.json"
            % datetime.datetime.utcnow().strftime("%Y-%m-%d-%H_%M_%S")
        )

        run_cmd = "packages "
        if os.path.isdir(source):
            run_cmd += "dir:"
        elif os.path.isfile(source):
            run_cmd += "file:"
        else:
            err("Invalid source: no such file of directory exists.")
            sys.exit(1)
        run_cmd += source
        run_cmd += " -o cyclonedx-json=%s" % sbom_file
        return run_cmd

    @staticmethod
    def print_version(tool):
        try:
            print_tool(
                "syft",
                subprocess.check_output([tool, "--version"]).decode().replace("\n", ""),
            )
        except:
            warn("syft: could not find tool version.")


def get_sbom_path(tool, tool_args):
    if tool == "syft":
        return Syft.get_sbom_path(tool_args)


def get_run_args(tool, source, sbom_name):
    if tool == "syft":
        return Syft.get_run_args(source, sbom_name)


def print_tool_version(tool):
    if tool.endswith("syft"):
        return Syft.print_version(tool)
