# SPDX-FileCopyrightText: 2023 Timesys Corporation
# SPDX-License-Identifier: MIT

import logging
import os
import timesys

from typing import List, Optional
from timesys.core.utils import save_file

logger = logging.getLogger(__name__)

ALMALINUX = ['AlmaLinux', 'AlmaLinux:8', 'AlmaLinux:9']
ALPINE = ['Alpine', 'Alpine:v3.10', 'Alpine:v3.11', 'Alpine:v3.12', 'Alpine:v3.13', 'Alpine:v3.14', 'Alpine:v3.15', 'Alpine:v3.16', 'Alpine:v3.17', 'Alpine:v3.18', 'Alpine:v3.19', 'Alpine:v3.2', 'Alpine:v3.20', 'Alpine:v3.3', 'Alpine:v3.4', 'Alpine:v3.5','Alpine:v3.6', 'Alpine:v3.7', 'Alpine:v3.8', 'Alpine:v3.9']
DEBIAN = ['Debian', 'Debian:10', 'Debian:11', 'Debian:12', 'Debian:13', 'Debian:3.0', 'Debian:3.1', 'Debian:4.0', 'Debian:5.0', 'Debian:6.0', 'Debian:7', 'Debian:8', 'Debian:9']
ROCKY = ['Rocky Linux', 'Rocky Linux:8', 'Rocky Linux:9']
UBUNTU = ['Ubuntu', 'Ubuntu:14.04:LTS', 'Ubuntu:16.04:LTS', 'Ubuntu:18.04:LTS', 'Ubuntu:20.04:LTS', 'Ubuntu:22.04:LTS', 'Ubuntu:23.10', 'Ubuntu:24.04:LTS', 'Ubuntu:Pro:14.04:LTS', 'Ubuntu:Pro:16.04:LTS', 'Ubuntu:Pro:18.04:LTS', 'Ubuntu:Pro:20.04:LTS', 'Ubuntu:Pro:22.04:LTS', 'Ubuntu:Pro:24.04:LTS']
OTHERS = ['Android', 'Bitnami', 'CRAN', 'GIT', 'GSD', 'GitHub Actions', 'Go', 'Hackage', 'Hex', 'Linux', 'Maven', 'NuGet', 'OSS-Fuzz', 'Packagist', 'Pub', 'PyPI', 'RubyGems', 'SwiftURL', 'UVI', 'crates.io', 'npm']

ALL_ECOSYSTEMS = OTHERS + ALMALINUX + ALPINE + DEBIAN + ROCKY + UBUNTU

def get_manifests():
    """Get all manifests that are accessible by the current user

    Group or folder tokens can be configured to limit results, but only one
    may be provided. If configured on the llapi object, folder token takes
    precedence.

    Returns
    -------
    list of dict
        Each manifest in the returned list is a dictionary with the following keys:
            manifest_name
                Name of the manifest
            manifest_token
                Token representing the manifest
            group_token
                Token representing the Group which the manifest belongs to
            folder_token
                Token representing the Folder which the manifest belongs to
            upload_date
                Date the manifest was uploaded


    """

    resource = "/api/v1/vigiles/manifests"
    data = {}

    folder_token = timesys.llapi.folder_token
    group_token = timesys.llapi.group_token

    if folder_token is not None:
        data["folder_token"] = folder_token
    elif group_token is not None:
        data["group_token"] = group_token

    return timesys.llapi.GET(resource, data_dict=data)


def get_manifest_info(manifest_token, sbom_format=None, file_format=None, sbom_version=None):
    """Get manifest data along with metadata

    Parameters
    ----------
    sbom_format : str, optional
        If specified, the server will convert the manifest data to this format.

        Acceptable formats are:
            "spdx"
                Convert the manifest to SPDX format
            "spdx-lite"
                Convert the manifest to a SPDX tag-value format
            "cyclonedx"
                Convert the manifest to CycloneDX JSON format

    file_format : str, optional
        Specify file format type for SPDX and CycloneDX SBOMs

    sbom_version : str, optional
        Specify SBOM version for SPDX and CycloneDX SBOMs

    Returns
    -------
    dict
        Result of the request with keys:
            manifest_token
                Token representing the manifest
            manifest_name
                Name of the manifest with the given token
            folder_token
                Token representing a Folder the manifest belongs to
            group_token
                Token representing a Group the manifest belongs to
            upload_date
                Date the manifest was uploaded
            manifest_data
                Contents of the manifest
                By default this is the same format as it was uploaded, unless
                converted using the "sbom_format" parameter
    """

    if not manifest_token:
        raise Exception("manifest_token is required")

    data = {}
    if sbom_format:
        data["sbom_format"] = sbom_format
    if file_format:
        data["file_format"] = file_format
    if sbom_version:
        data["sbom_version"] = sbom_version

    resource = f"/api/v1/vigiles/manifests/{manifest_token}"
    return timesys.llapi.GET(resource, data_dict=data)


def get_manifest_file(manifest_token, sbom_format=None, file_format=None, sbom_version=None):
    """Get manifest data as a file

    Response does not include other metadata such as group/folder tokens.

    Parameters
    ----------
    sbom_format : str, optional
        If specified, the server will convert the manifest data to this format.

        Acceptable formats are:
            "spdx"
                Convert the manifest to SPDX format
            "spdx-lite"
                Convert the manifest to a SPDX tag-value format
            "cyclonedx"
                Convert the manifest to CycloneDX JSON format

    file_format : str, optional
        Specify file format type for SPDX and CycloneDX SBOMs

    sbom_version : str, optional
        Specify SBOM version for SPDX and CycloneDX SBOMs

    Returns
    -------
    bytes
        The raw manifest file bytes
    """

    if not manifest_token:
        raise Exception("manifest_token is required")

    resource = f"/api/v1/vigiles/manifests/{manifest_token}"
    data = {'send_file': True}
    if sbom_format:
        data["sbom_format"] = sbom_format
    if file_format:
        data["file_format"] = file_format
    if sbom_version:
        data["sbom_version"] = sbom_version
    return timesys.llapi.GET(resource, data_dict=data, json=False)


def upload_manifest(manifest, kernel_config=None, uboot_config=None, manifest_name=None, 
                    subfolder_name=None, filter_results=False, extra_fields=None, upload_only=False, 
                    ecosystems=None, subscribe=None, export_format=None, export_path=None,
                    cyclonedx_format=None, cyclonedx_version=None):
    """Upload and scan (optionally) a manifest

    If a group_token is configured on the llapi object, it will be used as the upload location.
    Otherwise, the default is "Private Workspace."

    If both a group_token and folder_token are configured on the llapi object, the folder will
    be the upload location.

    A subfolder name can optionally be supplied in order to upload to or create a folder under the
    configured group and folder. This will then be the upload target for the given manifest.
    This is not supported for "Private Workspace".

    Parameters
    ----------
    manifest : str
        String of manifest data to upload
    kernel_config : str, optional
        Kernel config data used to filter out CVEs which are irrelevant to the built kernel
    uboot_config : str, optional
        Uboot config data used to filter out CVEs which are irrelevant to the built bootloader
    manifest_name : str, optional
        Name to give the new manifest. If not provided, one will be generated and returned.
    subfolder_name : str, optional
        If given, a new folder will be created with this name under the configured group or folder,
        and the manifest will be uploaded to this new folder. If the subfolder already exists, it will be uploaded there.
        Not supported for "Private Workspace" Group.
    filter_results : bool
        True to apply all configured filters to scan results, False to apply only kernel and uboot config filters.
        Default: False
        Note: These filters are configured through the Vigiles web interface.
    extra_fields : list of str, optional
        Optionally extend CVE data included in report with any of the following fields:
            "assigner", "description", "impact", "modified", "problem_types", "published", "references"
    upload_only : bool
        If true, do not generate an initial CVE report for the uploaded manifest
        Default: False
    ecosystems : list of ecosystems, optional
        If provided, the input ecosystems will be used to generate reports
    subscribe : str, optional
        If provided, the user will be subscribed to the notifications at the given frequency
        One of "none", "daily", "weekly", or "monthly"
    export_format: str, optional
        If provided, a vulnerability report will be downloaded at the specified path
        One of "pdf", "pdfsummary", "xlsx", "csv", "cyclonedx-vex", "cyclonedx-sbom-vex"
    export_path: str, optional
        If provided with export_format, will be used to save the vulnerability report
    cyclonedx_format: str, optional
        If export_format is selected as cyclonedx-vex or cyclonedx-sbom-vex, then this option is used to specify
        the format of the cyclonedx vex report
        One of "json", "xml"
    cyclonedx_version: str, optional
        If export_format is selected as cyclonedx-vex or cyclonedx-sbom-vex, then this option is used to specify
        the version of the cyclonedx vex report
        One of "1.4", "1.5", "1.6"

    Returns
    -------
    dict
        Results of scan with keys:

        manifest_token
            Token of the manifest which was scanned
        group_token
            Token of the group that the manifest belongs to
        folder_token
            Token of the folder that the manifest belongs to
        cves : list of dict
            list of dictionaries containing information about CVEs found in the scan, also referred to as the "report."
        counts : dict
            Dictionary containing CVE counts with keys:
                "fixed", "kernel", "toolchain", "unapplied", "unfixed", "upgradable", "whitelisted"
        date
            Date the scan was performed
        report_path
            URL where the report can be viewed on the web.
            The report token may also be split from the end of this string.
        exported_manifest
            The manifest data in SPDX format
    """

    if not manifest:
        raise Exception('manifest data is required')

    resource = "/api/v1/vigiles/manifests"

    data = {
        "manifest": manifest,
        "filter_results": filter_results,
        "upload_only": upload_only,
    }

    if kernel_config is not None:
        data["kernel_config"] = kernel_config

    if manifest_name is not None:
        data["manifest_name"] = manifest_name

    if uboot_config is not None:
        data["uboot_config"] = uboot_config

    if subfolder_name is not None:
        data["subfolder_name"] = subfolder_name

    if extra_fields is not None:
        if not isinstance(extra_fields, list) or not all(isinstance(i, str) for i in extra_fields):
            raise Exception("Parameter 'extra_fields' must be a list of strings") from None
        data["with_field"] = extra_fields  # will be split into repeated params

    if ecosystems is not None:
        ecosystems_str = ecosystems
        ecosystems = []
        if ecosystems_str.lower() == "all":
            ecosystems = ALL_ECOSYSTEMS
        else:
            invalid_ecosystems = set()
            ecosystems = [esys.strip() for esys in ecosystems_str.split(",")]
            for ecosystem in ecosystems:
                if ecosystem not in ALL_ECOSYSTEMS:
                    invalid_ecosystems.add(ecosystem)
            if invalid_ecosystems:
                logger.warning('Skipping invalid ecosystems: %s. Refer to README.md for valid ecosystems.' % ",".join(invalid_ecosystems))
            ecosystems = [item for item in ecosystems if item not in invalid_ecosystems]
        data["ecosystems"] = ",".join(ecosystems)

    if subscribe is not None:
        data["subscribe"] = subscribe

    group_token = timesys.llapi.group_token
    folder_token = timesys.llapi.folder_token
    if folder_token:
        data["folder_token"] = folder_token
    if group_token:
        data["group_token"] = group_token
    else:
        logger.warning('No group token is configured. Upload target will be "Private Workspace"')

    if not group_token and (folder_token or subfolder_name):
        logger.warning('"Private Workspace" does not support folders. Since a group token is not configured, the folder_token and subfolder_name arguments will be ignored.')

    if export_format:
        data["export_format"] = export_format

    if cyclonedx_format:
        data["cyclonedx_format"] = cyclonedx_format

    if cyclonedx_version:
        data["cyclonedx_version"] = cyclonedx_version

    result = timesys.llapi.POST(resource, data)

    exported_report_data = result.pop("exported_report")
    if exported_report_data:
        file_extension = export_format
        if file_extension.startswith('pdf'):
            file_extension = file_extension[:3]
        elif file_extension.startswith('cyclonedx'):
            file_extension = cyclonedx_format
        
        root, _ = os.path.splitext(export_path)
        export_path = "%s.%s" % (root, file_extension)

        try:
            save_file(exported_report_data, export_path)
            logger.info("Exported report saved to %s" % export_path)
        except Exception as e:
            logger.error(f"Error occured while saving report file: {e}")

    return result


def rescan_manifest(manifest_token, rescan_only=False, filter_results=False, extra_fields=None):
    """Generate a new report for the given manifest_token

    Parameters
    ---------
    manifest_token : str
        Token for the manifest to rescan
    rescan_only : bool
        If True, rescan the manifest but not return the report data
        Default: False
    filter_results : bool
        Apply all filters to report if True, else only config filters if available.
        Default: False
    extra_fields : list of str, optional
        Optionally extend CVE data included in report with any of the following fields:
            "assigner", "description", "impact", "modified", "problem_types", "published", "references"

    Returns
    -------
    dict
        Results of scan with keys:

        manifest_token
            Token of the manifest which was scanned
        group_token
            Token of the group that the manifest belongs to
        folder_token
            Token of the folder that the manifest belongs to
        cves : list of dict
            list of dictionaries containing information about CVEs found in the scan, also referred to as the "report."
        counts : dict
            Dictionary containing CVE counts with keys:
                "fixed", "kernel", "toolchain", "unapplied", "unfixed", "upgradable", "whitelisted"
        date
            Date the scan was performed
        report_path
            URL where the report can be viewed on the web.
            The report token may also be split from the end of this string.
        exported_manifest
            The manifest data in SPDX format
    """
    if not manifest_token:
        raise Exception('manifest_token is required')

    resource = f"/api/v1/vigiles/manifests/{manifest_token}/reports"
    data = {
        "manifest": manifest_token,
        "rescan_only": rescan_only,
        "filtered": filter_results,
    }

    if extra_fields is not None:
        if not isinstance(extra_fields, list) or not all(isinstance(i, str) for i in extra_fields):
            raise Exception("Parameter 'extra_fields' must be a list of strings") from None
        data["with_field"] = extra_fields  # will be split into repeated params

    return timesys.llapi.POST(resource, data)


def delete_manifest(manifest_token, confirmed=False):
    """Delete a manifest with the given token

    This action can not be undone. It requires passing True for the
    'confirmed' keyword parameter to prevent accidental use.

    Parameters
    ---------
    manifest_token : str
        Token of the manifest to be deleted

    Returns
    -------
    dict
        success : bool
            True or False depending on result of operation
        message : str
            Reason when "success" is False. May refer to additional keys in response.

    Notes
    -----
    This action can not be undone!
    """

    if not manifest_token:
        raise Exception("manifest_token is required")

    resource = f"/api/v1/vigiles/manifests/{manifest_token}"
    data = {"confirmed": confirmed}
    return timesys.llapi.DELETE(resource, data_dict=data)


def get_report_tokens(manifest_token):
    """Get a list of report_tokens available for the given manifest_token

    Parameters
    ----------
    manifest_token : str
        Token of the manifest for which to retrieve a list of available reports

    Returns
    -------
    dict
        A dictionary with meta info about the requested manifest and a list of report info

        dictionaries, each of which contain the keys:
            "created_date", "report_token", "manifest_token", "manifest_version"
    """

    if not manifest_token:
        raise Exception("manifest_token is required")

    resource = f"/api/v1/vigiles/manifests/{manifest_token}/reports"
    return timesys.llapi.GET(resource)


def get_latest_report(manifest_token, filter_results=False, extra_fields=None):
    """Download the latest report for a manifest with the given token.

    Parameters
    ----------
    manifest_token : str
        Token of the manifest for which to fetch the latest report
    filter_results : bool
        apply all filters to report if True, else only config filters.
        Default: False
    extra_fields : list of str, optional
        Optionally extend CVE data included in report with any of the following fields:
            "assigner", "description", "impact", "modified", "problem_types", "published", "references"

    Returns
    -------
    dict
        Results of scan with keys:

        manifest_token
            Token of the manifest which was scanned
        group_token
            Token of the group that the manifest belongs to
        folder_token
            Token of the folder that the manifest belongs to
        cves : list of dict
            list of dictionaries containing information about CVEs found in the scan, also referred to as the "report."
        counts : dict
            Dictionary containing CVE counts with keys:
                "fixed", "kernel", "toolchain", "unapplied", "unfixed", "upgradable", "whitelisted"
        date
            Date the scan was performed
        group_path
            URL where the group can be viewed on the web.
        report_path
            URL where the report can be viewed on the web.
            The report token may also be split from the end of this string.

    """

    if not manifest_token:
        raise Exception("manifest_token is required")

    data = {
        'filtered': filter_results,
    }

    if extra_fields is not None:
        if not isinstance(extra_fields, list) or not all(isinstance(i, str) for i in extra_fields):
            raise Exception("Parameter 'extra_fields' must be a list of strings") from None
        data["with_field"] = extra_fields  # will be split into repeated params

    resource = f"/api/v1/vigiles/manifests/{manifest_token}/reports/latest"
    return timesys.llapi.GET(resource, data_dict=data)


def set_custom_score(manifest_token, product_name, cve_id, custom_score, product_version=None):
    """Set cve custom score in manifest chain.

    Parameters
    ----------
    manifest_token : str
        Token of the manifest used to set a custom score on the related chain
    product_name : str
        Target CPE Product (package_name) name
    cve_id : str
        CVE ID for which you would like to set a custom score
    custom_score : str
        custom score value to set
    product_version : str, optional
        Target product version

    Returns
    -------
    dict
        success : bool
            True or False depending on result of operation
        message : str
            Custom CVE score updated.

    """

    if not all([product_name, cve_id, custom_score, manifest_token]):
        raise Exception("Missing required data from: { product_name, cve_id, custom_score, manifest_token }")


    data = {
        'package_name': product_name,
        'cve_id': cve_id,
        'custom_score': custom_score,
    }

    if product_version is not None:
        data['package_version'] = product_version

    resource = f"/api/v1/vigiles/manifests/{manifest_token}/custom_scores"
    return timesys.llapi.POST(resource, data_dict=data)


def bulk_move_manifests(
    sbom_tokens: List[str], 
    target_group_token: Optional[str] = None, 
    target_folder_token: Optional[str] = None, 
    include_history: bool = False
):
    """Move multiple SBOMs to a group/folder

    Parameters
    ----------
    sbom_tokens : List[str]
        List of SBOM tokens to move
    target_group_token : str, optional
        Target group token to which the sboms are to be moved, by default None
    target_folder_token : str, optional
        Target folder token to which the sboms are to be moved, by default None
    include_history : bool, optional
        Include previous versions of the SBOM, by default False
    """
    if not any([target_group_token, target_folder_token]):
        raise Exception("Please specify either a target group or target folder token")
    
    data = {
        "sbom_tokens": sbom_tokens,
        "copy": False,
        "include_history": include_history
    }
    
    if target_folder_token:
        data['target_folder_token'] = target_folder_token
    if target_group_token:
        data['target_group_token'] = target_group_token
    resource = "/api/v1/vigiles/manifests/bulk-options/move"
    return timesys.llapi.POST(resource, data_dict=data)


def bulk_copy_manifests(
    sbom_tokens: List[str], 
    target_group_token: Optional[str] = None, 
    target_folder_token: Optional[str] = None, 
    include_history: bool = False
):
    """Copy multiple SBOMs to a group/folder

    Parameters
    ----------
    sbom_tokens : List[str]
        List of SBOM tokens to copy
    target_group_token : str, optional
        Target group token to which the sboms are to be copied, by default None
    target_folder_token : str, optional
        Target folder token to which the sboms are to be copied, by default None
    include_history : bool, optional
        Include previous versions of the SBOM, by default False
    """
    if not any([target_group_token, target_folder_token]):
        raise Exception("Please specify either a target group or target folder token")
    
    data = {
        "sbom_tokens": sbom_tokens,
        "copy": True,
        "include_history": include_history
    }
    
    if target_folder_token:
        data['target_folder_token'] = target_folder_token
    if target_group_token:
        data['target_group_token'] = target_group_token
    resource = "/api/v1/vigiles/manifests/bulk-options/move"
    return timesys.llapi.POST(resource, data_dict=data)