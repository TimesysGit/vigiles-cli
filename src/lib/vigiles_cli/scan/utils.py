# SPDX-FileCopyrightText: 2023 Timesys Corporation
# SPDX-License-Identifier: MIT

import os
import sys


Vigiles_Debug = False
Vigiles_Verbose = True
Previous_Verbose = True

UNKNOWN = "unknown"
UNSET = "unset"


def set_debug(enable=True):
    global Vigiles_Debug, Vigiles_Verbose, Previous_Verbose
    Vigiles_Debug = enable
    if enable:
        Previous_Verbose = Vigiles_Verbose
        Vigiles_Verbose = True
    else:
        Vigiles_Verbose = Previous_Verbose


def _print_list(tag, s_list, fp=sys.stdout):
    msg = "\n\t".join(s_list)
    print("Vigiles %s: %s" % (tag, msg), file=fp)


def dbg(msg, extra=[]):
    global Vigiles_Debug
    if Vigiles_Debug:
        s_list = [msg] + extra
        _print_list("DEBUG", s_list)


def info(msg, extra=[]):
    global Vigiles_Verbose
    if Vigiles_Verbose:
        s_list = [msg] + extra
        _print_list("INFO", s_list)


def warn(msg, extra=[]):
    s_list = [msg] + extra
    _print_list("WARNING", s_list, fp=sys.stderr)


def err(msg, extra=[]):
    if not isinstance(msg, list):
        msg = [msg]
    s_list = msg + extra
    _print_list("ERROR", s_list, fp=sys.stderr)


def cmd_exists(cmd, path=None):
    """test if a path contains an executable file with name"""
    if path is None:
        path = os.environ["PATH"].split(os.pathsep)

    for prefix in path:
        filename = os.path.join(prefix, cmd)
        executable = os.access(filename, os.X_OK)
        is_not_directory = os.path.isfile(filename)
        if executable and is_not_directory:
            return True
    return False


def print_tool(tool, msg, fp=sys.stdout):
    print("%s: %s" % (os.path.basename(tool), msg), file=fp)
