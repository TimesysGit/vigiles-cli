# Timesys Vigiles CLI

This project contains a command-line tool for interacting with [Vigiles](https://www.timesys.com/solutions/vigiles-vulnerability-management/) APIs.

The server-side API endpoint documentation for Vigiles is [here](https://linuxlink.timesys.com/docs/vigiles-api-manual).

### Install

From this repository, you can install with pip:

```
pip3 install .
```

Generate HTML docs from the source:

```
pip3 install .[docs]
```

### Setup

Usage of the APIs requires a [Key
file](https://linuxlink.timesys.com/docs/wiki/engineering/LinuxLink_Key_File)
for authentication. The key file contains the user's email address and
API key.

For configuring the Vigiles CLI to use specific Product or Folder
locations, refer to the [Dashboard
Config](https://linuxlink.timesys.com/docs/vigiles-vulnerability-monitoring-and-management-user-guide#Dashboard-config)
documentation. Dashboard Config files can be downloaded from Product pages
on the [Vigiles Dashboard](https://linuxlink.timesys.com/vigiles/) 

### Getting Started

#### Command Line

This tool is installed as the command `vigiles`. 
To get started with the command line, try specifying a keyfile and checking the `heartbeat` command, which should look like this:

```
$ vigiles -k /path/to/linuxlink_key heartbeat
{'ok': True}
```

Note: If you put the Key File in the default location ($HOME/timesys/linuxlink_key), you don't need the '-k' option.


Vigiles Scanner (scan command)
==============================

This Vigiles CLI sub-command is useful for SBOM generation (through Timesys recommended SBOM generator tools) and Vulnerability reporting with the 
**[Timesys Vigiles](https://www.timesys.com/security/vigiles/)** product offering.

Supported SBOM generator tools
==============================
 - [SYFT<sup>TM</sup>](https://github.com/anchore/syft) 
 
> NOTE: refer to individual SBOM generator tool documentation to learn installation and setup procedure and tool-supported arguments and usage


Using Vigiles Scanner
=======================

To generate a vulnerability report, follow the below steps: 


1. Run the **Vigiles Scanner** (vigiles scan) to search for Timesys recommended SBOM generator tool for your ecosystem
    ```sh
    vigiles scan -e "{ecosystem}"
    ```

    > Example:
    > 
    >```vigiles scan -e python```

2. Run **Vigiles Scanner** (vigiles scan) with your selection of **SBOM generator tool**, and **source**.

    > NOTE: Ensure that the SBOM generator tool you want to use it with is already
      **```installed and configured```** (You may find additional instructions for the SBOM generator tool in 
      the link given under the ```Supported SBOM generator tools``` section).

    ```sh
    vigiles scan -t {name of SBOM generator tool} -s {source to scan for SBOM generation}
    ```

    > Example:
    > 
    >```vigiles scan -t syft -s /myproject```
    > 
    > Note: valid tool names are restricted to tools written in the *Supported SBOM generator tools* section.

3. View the Vigiles Vulnerability (Text) Report Locally

    The vulnerability report will be created in the current working directory with the file naming format
    ```vulnerability-report-{timestamp}.txt``` e.g.:
    ```sh
    wc -l vulnerability-report-2023-05-02-10_45_03.txt
        2900 vulnerability-report-02052023.txt
    ```

4. View the Vigiles Vulnerability Online Report

    The local vulnerability text report will contain a link to a comprehensive and graphical report, e.g.:
    ```
    -- Vigiles Vulnerability Report --
            View detailed online report at:
              https://linuxlink.timesys.com/cves/reports/<Unique Report Identifier>
    ```

### Disclaimer
* **SYFT** is a trademark of **Anchore, Inc**
