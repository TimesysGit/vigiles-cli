Timesys Vigiles CLI
===================

This project contains a command-line tool for interacting with APIs for Timesys services such as `Vigiles <https://www.timesys.com/solutions/vigiles-vulnerability-management/>`_.


Requirements
============

Usage of the APIs requires a `Key file <https://linuxlink.timesys.com/docs/wiki/engineering/LinuxLink_Key_File>`_ for authentication. The key file contains the user's email address and API key.

For configuring the Vigiles subpackage to use specific Product or Folder locations, refer to the `Dashboard Config <https://linuxlink.timesys.com/docs/vigiles-vulnerability-monitoring-and-management-user-guide#Dashboard-config>`_ documentation. Dashboard Config files are downloaded from Product pages on the `Vigiles Dashboard <https://linuxlink.timesys.com/vigiles/>`_.


Vigiles Scanner (scan command)
==============================

This Vigiles-cli sub-command is useful for SBOM generation (through Timesys recommended SBOM generator tools) and Vulnerability reporting with
`Timesys Vigiles <https://www.timesys.com/security/vigiles/>`_ product offering.

Supported SBOM generator tools
==============================
 - `syft <https://github.com/anchore/syft>`_

NOTE: refer to individual SBOM generator tool documentation to learn installation and setup procedure and tool-supported arguments and usage


Using Vigiles Scanner
=======================

To generate a vulnerability report, follow the below steps:


1. Run **Vigiles Scanner** (vigiles scan) to search for Timesys recommended SBOM generator tool for your ecosystem

.. code-block:: bash

    vigiles scan -e "{ecosystem}"

    Example:
    vigiles scan -e python

2. Run **Vigiles Scanner** (vigiles scan) with your selection of **SBOM generator tool**, and **source**.

   NOTE: Before this step ensure that the SBOM generator tool you want to use it with is already
   *installed/set up* (you may find installation/setup instructions for the SBOM generator tool in
   the link given under the *Supported SBOM generator tools* section).

.. code-block:: bash

    vigiles scan -t {name of SBOM generator tool} -s {source to scan for SBOM generation}

    Example:
    vigiles scan -t syft -s /myproject


   Note: valid tool names are restricted to tools written in the Supported SBOM generator
   tools section.

   The Vigiles scan sets the SBOM generator tool arguments be default.
   To override them, refer to the *Expert mode* section.

3. View the Vigiles Vulnerability (Text) Report Locally

   The vulnerability report will be created in the current working directory with the file naming format
   *vulnerability-report-{timestamp}.txt* e.g.:

.. code-block:: bash

    wc -l vulnerability-report-2023-05-02-10_45_03.txt
        2900 vulnerability-report-02052023.txt

4. View the Vigiles Vulnerability Online Report

   The local vulnerability text report will contain a link to a comprehensive and graphical report, e.g.:

.. code-block:: bash

    -- Vigiles Vulnerability Report --
            View detailed online report at:
              https://linuxlink.timesys.com/cves/reports/<Unique Report Identifier>

Expert Mode
===========

In place of the **Vigiles Scanner** (vigiles scan) to set SBOM generator tool arguments by default,
you can override default arguments and set it on your own with the Expert mode configurations.

SBOM generation tool arguments could be set with **-a / --sbom-tool-args**.

.. code-block:: bash

    vigiles scan -t {name of SBOM generator tool} -a "{SBOM generation tool arguments}"

    Example:
    vigiles scan -t syft -a "packages dir:/home/user/myproject -o cyclonedx-json=myproject.json"


Other Expert Mode Configurations
================================

SBOM generator tool binary directory
====================================

**Vigiles Scanner** (vigiles scan) searches for the SBOM tool binary executable in the system bin paths and
the current directory.

In case the SBOM tool binary is not in them then a binary path must be set with the Vigiles Scanner argument
**-p / --sbom-tool-dir**.

.. code-block:: bash

   Example:
   -p /home/user

   Or

   --sbom-tool-dir /home/user


SBOM path
=========

**Vigiles Scanner** (vigiles scan) finds the path of the generated SBOM from
**SBOM generator tool arguments (-a or --sbom-tool-args)**.
It should work in most cases.
However, if you run into a situation where vulnerability report generation fails, because it cannot accurately
find the SBOM path, you can set the SBOM path with **-m / --sbom**.

.. code-block:: bash

   Example:

   -m /home/user/cyclonedxq-sbom.json

   Or

   --sbom /home/user/cyclonedxq-sbom.json

Custom SBOM naming
==================

You can override the default SBOM name with a custom name using **-N / --name** argument of
**Vigiles Scanner** (vigiles scan).

.. code-block:: bash

   Example:

   -N Custom-Name

   Or

   --name Custom-Name


Vulnerability report naming
===========================

By default, **Vigiles Scanner** (vigiles scan) stores the vulnerability report in the current working directory.
The file naming format is *vulnerability-report-{timestamp}.txt*.
You can change it to a custom file name and path with **-o / --outfile**.

.. code-block:: bash

   Example:

   -o /home/user/my-vulnerability-report.txt

   Or

   --outfile /home/user/my-vulnerability-report.txt


Dynamic subfolder creation
==========================

If a Dashboard Config is used, a subfolder name can be specified for dynamic folder creation by the Vigiles
Scanner argument **--subfolder**.
SBOM will be uploaded to a subfolder with this name within the location specified in the Dashboard Config.
If one does not exist, it will be created.
This option will be overridden by the environment variable *VIGILES_SUBFOLDER_NAME*

.. code-block:: bash

   Example:

   -F mysubfolder

   Or

   --subfolder mysubfolder


Debug
=====

For development purposes, debugging messages can be enabled with **-D / --enable-debug**
and SBOM generator tool version can be printed with **--version**.

.. toctree::
   :maxdepth: 4
   :caption: Package Contents:

   modules


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
