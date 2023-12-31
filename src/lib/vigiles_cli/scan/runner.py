# SPDX-FileCopyrightText: 2023 Timesys Corporation
# SPDX-License-Identifier: MIT

import datetime
import os
import shlex
import subprocess
import sys
import urllib.parse

from .constants import VIGILES_SUPPORTED_TOOLS
from .sbom_tools import get_sbom_path, get_run_args, print_tool_version
from .utils import set_debug, dbg, err, info, cmd_exists, print_tool
import vigiles_cli.core as timesys

NVD_BASE_URL = "https://nvd.nist.gov/vuln/detail/"
API_DOC = "https://linuxlink.timesys.com/docs/wiki/engineering/LinuxLink_Key_File"
INFO_PAGE_DOMAIN = "https://www.timesys.com"
INFO_PAGE_PATH = "/security/vulnerability-patch-notification/"
INFO_PAGE = INFO_PAGE_DOMAIN + INFO_PAGE_PATH


def get_usage():
    return (
        "This command generates an SBOM using the tool selected by the user. "
        "The generated SBOM is then uploaded to Vigiles "
        "to check the vulnerability status of the provided components. \n\n"
        "To generate a vulnerability report a LinuxLink API keyfile, and an active Vigiles "
        "subscription is required.\n\n"
        "See this document for keyfile information:\n"
        "%s\n\n"
        "NOTE: SBOM generator tool should already by installed." % API_DOC
    )


def print_sbom_tools(tools, search=None):
    if search:
        tools = {
            tool: ecosystem
            for tool, ecosystem in tools.items()
            if search.lower() in ecosystem.get("ecosystems", [])
        }

    if not tools:
        err(
            "No recommendations were found for ecosystem '%s'. Contact the Vigiles team to request support."
            % search
        )
        sys.exit(1)

    print("*" * 80)
    print("\n\tList of Timesys recommended SBOM generator tools \n")
    print("*" * 80)
    if search:
        print("%-18s %-12s %s" % ("Name", "Ecosystem", "URL"))
    else:
        print("%-25s %s" % ("Name", "Ecosystems"))
    print("-" * 80)
    for tool, ecosystems in tools.items():
        if search:
            print("%-18s %-12s %s" % (tool, search, ecosystems.get("url", [])))
        else:
            print("%-25s %s" % (tool, ",".join(ecosystems.get("ecosystems", []))))
    print("-" * 80)
    if search:
        print(
            "NOTE: Refer to tool URLs to get more details about their capabilities and setup\n"
            "      procedures.\n"
        )
    return


def parse_args(args):
    set_debug(args.debug)

    if args.debug:
        args_list = ["%s=%s" % (k, v) for k, v in vars(args).items()]
        dbg("Running Vigiles scan with arguments - ")
        for arg in args_list:
            dbg("\t %s" % arg)

    if args.list_tools or args.ecosystem:
        search_str = None
        if args.ecosystem:
            search_str = args.ecosystem
        print_sbom_tools(VIGILES_SUPPORTED_TOOLS, search_str)
        sys.exit(0)

    sbom_tool_args = args.sbom_tool_args
    if args.tool is None:
        err("The following arguments are required: -t/--tool")
        exit(1)
    elif args.tool not in VIGILES_SUPPORTED_TOOLS.keys():
        err("The SBOM generator tool '%s' is currently not supported." % args.tool)
        sys.exit(1)
    elif args.tool in VIGILES_SUPPORTED_TOOLS.keys() and VIGILES_SUPPORTED_TOOLS[args.tool]["ref_only"]:
        info("Refer to the tool's URL '%s' for setup and usage." % VIGILES_SUPPORTED_TOOLS[args.tool]["url"])
        sys.exit(1)
    elif args.tool and args.sbom_tool_args is None:
        dbg("No SBOM tool args provided. Finding tool args.")
        try:
            sbom_tool_args = get_run_args(args.tool, args.source, args.sbom_name)
            dbg("SBOM tool args - '%s' ." % sbom_tool_args)
        except Exception as _:
            err("The following arguments are required: -a/--sbom-tool-args .")
            exit(1)

    tool_path = args.tool
    if not cmd_exists(args.tool):
        if not args.sbom_tool_dir:
            err(
                "The SBOM generator tool '%s' was not found in system binary paths. \n"
                "To specify a path use the -p argument." % args.tool
            )
            sys.exit(1)
        else:
            if not os.path.exists(args.sbom_tool_dir):
                err(
                    "SBOM generator tool directory '%s' doesn't exist."
                    % args.sbom_tool_dir
                )
                sys.exit(1)
            elif args.tool not in os.listdir(args.sbom_tool_dir):
                err(
                    "Missing tool '%s' in SBOM generator tool directory '%s'."
                    % (args.tool, args.sbom_tool_dir)
                )
                sys.exit(1)

        tool_path = os.path.join(args.sbom_tool_dir, args.tool)

    if args.version:
        print_tool_version(tool_path)
        exit(0)

    if args.sbom:
        sbom = args.sbom
    else:
        try:
            sbom = get_sbom_path(args.tool, sbom_tool_args)
            dbg("SBOM - '%s' ." % sbom)
        except Exception as _:
            err(
                "Could not find the path of the SBOM file to be generated by the SBOM tool. Provide it with -s argument."
            )
            sys.exit(1)

    outfile = args.outfile
    if not args.outfile:
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d-%H_%M_%S")
        outfile = "vulnerability-report-%s.txt" % timestamp

    vgls_scan_args = {
        "tool": tool_path,
        "sbom_tool_args": sbom_tool_args,
        "sbom_tool_dir": args.sbom_tool_dir,
        "subfolder_name": args.subfolder_name,
        "sbom": sbom,
        "report": outfile,
        "sbom_name": args.sbom_name,
    }

    return vgls_scan_args


def read_sbom(sbom_file):
    try:
        with open(sbom_file, "r") as f:
            sbom_data = "".join(line.rstrip() for line in f)
    except (OSError, IOError, UnicodeDecodeError) as e:
        err("Error: Could not open SBOM: '%s' ." % e)
        sys.exit(1)
    return sbom_data


def print_cves(result, outfile=None):
    cves = result.get("cves", {})
    if cves:
        print("\n\n-- Component CVEs --", file=outfile)
        for pkg, info in cves.items():
            for cve in info:
                print("\n\tComponent:  %s" % pkg, file=outfile)
                print("\tVersion: %s" % cve["version"], file=outfile)
                print("\tCVE ID:  %s" % cve["cve_id"], file=outfile)
                print("\tURL:     %s%s" % (NVD_BASE_URL, cve["cve_id"]), file=outfile)
                print("\tCVSSv3:  %s" % cve["cvss"], file=outfile)
                print("\tVector:  %s" % cve["vector"], file=outfile)
                print("\tStatus:  %s" % cve["status"], file=outfile)
                patches = cve.get("fixedby")
                if patches:
                    print("\tPatched by:", file=outfile)
                    for patch in patches:
                        print("\t* %s" % patch, file=outfile)


def parse_unfixed_cve_counts(counts):
    total = (
        counts.get("unfixed", 0)
        + counts.get("unapplied", 0)
        + counts.get("upgradable", 0)
    )
    kernel = (
        counts.get("kernel", {}).get("unfixed", 0)
        + counts.get("kernel", {}).get("unapplied", 0)
        + counts.get("kernel", {}).get("upgradable", 0)
    )
    userspace = total - kernel
    return {"total": total, "userspace": userspace, "kernel": kernel}


def parse_fixed_cve_counts(counts):
    total = counts.get("fixed", 0)
    kernel = counts.get("kernel", {}).get("fixed", 0)
    userspace = total - kernel
    return {"total": total, "userspace": userspace, "kernel": kernel}


def parse_cvss_counts(counts):
    high_cvss_total = counts.get("high", {}).get("unfixed", 0)
    high_cvss_kernel = counts.get("kernel", {}).get("high", {}).get("unfixed", 0)
    critical_cvss_total = counts.get("critical", {}).get("unfixed", 0)
    critical_cvss_kernel = (
        counts.get("kernel", {}).get("critical", {}).get("unfixed", 0)
    )
    total = high_cvss_total + critical_cvss_total
    kernel = high_cvss_kernel + critical_cvss_kernel
    userspace = total - kernel
    return {"total": total, "userspace": userspace, "kernel": kernel}


def print_report_header(result, f_out=None):
    from datetime import datetime

    report_time = result.get("date", datetime.utcnow().isoformat())

    print("-- Vigiles Vulnerability Scanner --\n\n" "\t%s\n\n" % INFO_PAGE, file=f_out)
    print("-- Date Generated (UTC) --\n", file=f_out)
    print("\t%s" % report_time, file=f_out)


def print_report_overview(result, f_out=None):
    report_path = result.get("report_path", "")
    product_path = result.get("product_path", "")

    if report_path:
        report_url = urllib.parse.urljoin(timesys.llapi.url, report_path)
        print("\n-- Vigiles Vulnerability Report --", file=f_out)
        print("\n\tView detailed online report at:\n" "\t  %s" % report_url, file=f_out)
    elif product_path:
        product_url = urllib.parse.urljoin(timesys.llapi.url, product_path)
        product_name = result.get("product_name", "Default")
        print("\n-- Vigiles Dashboard --", file=f_out)
        print(
            "\n\tThe SBOM has been uploaded to the '%s' Product Workspace:\n\n"
            "\t  %s\n" % (product_name, product_url),
            file=f_out,
        )


def print_summary(result, outfile=None):
    def show_subscribed_summary(f_out=outfile):
        counts = result.get("counts", {})
        unfixed = parse_unfixed_cve_counts(counts)
        fixed = parse_fixed_cve_counts(counts)

        cvss_counts = counts.get("cvss_counts", {})
        cvss = parse_cvss_counts(cvss_counts)

        print(
            "\n\tUnfixed: {} ({} User space, {} Kernel)".format(
                unfixed["total"],
                unfixed["userspace"],
                unfixed["kernel"],
            ),
            file=f_out,
        )
        print(
            "\tFixed: {} ({} User space, {} Kernel)".format(
                fixed["total"], fixed["userspace"], fixed["kernel"]
            ),
            file=f_out,
        )
        print(
            "\tHigh/Critical CVSS (Unfixed): {} ({} User space, {} Kernel)".format(
                cvss["total"], cvss["userspace"], cvss["kernel"]
            ),
            file=f_out,
        )

    if "counts" in result:
        show_subscribed_summary(outfile)


def vigiles_request(vgls_chk):
    resource = "/api/v1/vigiles/manifests"

    sbom_path = vgls_chk.get("sbom", "")
    sbom_name = vgls_chk.get("sbom_name", "")
    report_path = vgls_chk.get("report", "")
    product_token = timesys.llapi.product_token if timesys.llapi.product_token else ""
    folder_token = timesys.llapi.folder_token if timesys.llapi.folder_token else ""
    subfolder_name = (
        vgls_chk.get("subfolder_name", "") if vgls_chk.get("subfolder_name") else ""
    )

    if report_path:
        outfile = open(report_path, "w")
    else:
        outfile = None

    # read sbom
    sbom_data = ""
    if sbom_path:
        sbom_data = read_sbom(sbom_path)

    data = {
        "manifest": sbom_data,
        "product_token": product_token,
        "folder_token": folder_token,
        "subfolder_name": subfolder_name,
        "upload_only": False,
        "subscribe": False,
    }

    if sbom_name:
        data.update({"manifest_name": sbom_name})

    if not timesys.llapi.dry_run:
        print("Vigiles: Requesting SBOM analysis from Vigiles ...\n", file=sys.stderr)

    result = timesys.llapi.POST(resource, data)
    if not result or timesys.llapi.dry_run is True:
        if timesys.llapi.dry_run:
            print(result)
        if outfile:
            outfile.close()
        sys.exit(1)

    print_report_header(result, outfile)
    print_report_overview(result, outfile)
    print_summary(result, outfile=outfile)
    print_cves(result, outfile=outfile)

    if outfile is not None:
        print_report_overview(result)
        print_summary(result)
        print("\n\tLocal summary written to:\n\t  %s" % os.path.relpath(outfile.name))
        outfile.close()


def run_tool(tool, sbom_tool_args, sbom):
    # cleanup old sbom if already exist in the location
    if os.path.exists(sbom):
        os.remove(sbom)

    # print tool version
    print_tool_version(tool)

    # run tool
    print_tool(tool, "Running with arguments '%s'" % sbom_tool_args)

    cmd_str = "%s %s" % (tool, sbom_tool_args)
    cmd = shlex.split(cmd_str)

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    for c in iter(lambda: process.stdout.read(1), b""):
        sys.stdout.buffer.write(c)

    if not os.path.exists(sbom):
        err("Could not generate SBOM file: '%s' ." % sbom)
        sys.exit(1)

    print_tool(tool, "Generated SBOM '%s' ." % sbom)
    return


def runner(parsed_args):
    vgls_scan = parse_args(parsed_args)
    run_tool(
        vgls_scan.get("tool"), vgls_scan.get("sbom_tool_args"), vgls_scan.get("sbom")
    )
    return vigiles_request(vgls_scan)
