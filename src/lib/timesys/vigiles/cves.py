# SPDX-FileCopyrightText: 2023 Timesys Corporation
# SPDX-License-Identifier: MIT

import timesys


def get_cve_info(cve_id, fields=None):
    """Get CVE info by CVE ID

    Parameters
    ----------
    cve_id : str
        A valid CVE ID
    fields: list of str, optional
        Limit cve data returned to given the fields. If none are specified, all are returned.

        Valid fields:
            "affected_configurations", "assigner", "description", "identifier", "impact", "modified", "problem_types", "published", "references" , "nvd_status", "cisa", "epss", "aliases"

    Returns
    -------
    dict
        CVE data, optionally filtered to the requested fields
    """
    if not cve_id:
        raise Exception("cve_id is required")

    resource = f"/api/v1/vigiles/cves/{cve_id}"
    data = {}
    if fields is not None:
        data["fields"] = fields

    return timesys.llapi.GET(resource, data_dict=data)


def search_cves_by_product(cpe_product, version="", ids_only=False):
    """Get CVEs which affect given CPE Product and optionally filter by version

    Parameters
    ----------
    product : str
        CPE Product (package_name) to search CVEs for
    version : str, optional
        Version of the product to filter results by, else all affected versions
    ids_only : bool
        Return list of CVE identifiers only, no descriptions.
        Default: False

    Returns
    -------
    list or dict
        A list of CVE ids is returned if "ids_only" is true, otherwise a dictionary with CVE identifier keys and description values
    """

    if not cpe_product:
        raise Exception('cpe_product is required')

    resource = "/api/v1/vigiles/cves"
    data = {
        "product": cpe_product,
        "version": version,
        "ids_only": ids_only,
    }
    return timesys.llapi.GET(resource, data_dict=data)


def set_status(scope, cve_id, package_name, status, justification=None, justification_detail=None, package_version=None, manifest_tokens=None, group_tokens=None):
    """Update the vulnerability status of a CVE

    Parameters
    ----------
    scope : str
        Scope of the vulnerability update

        "manifest", "group", "all"
    cve_id : str
        A valid vulnerability ID
    package_name : str
        Name of package for which status is to be set
    status : str
        Status to be set

        "resolved", "resolved_with_pedigree", "exploitable", "in_triage", "false_positive", "not_affected"
    justification : str, optional
        Justification for the status to be set
        Default: None

        "code_not_present", "code_not_reachable", "requires_configuration", "requires_dependency", "requires_environment", "protected_by_compiler", "protected_at_runtime", "protected_at_perimeter", "protected_by_mitigating_control"
    justification_detail : str, optional
        Detailed justification for the status to be set
        Default: None
    package_version : str, optional
        Version of package for which status is to be set
        Default: "all"
    manifest_tokens : list[str], optional
        If the scope is "manifest", the list of manifest tokens to update
        Default: None
    group_tokens : list[str], optional
        If the scope is "group", the list of group tokens to update

    Returns
    -------
    dict
        All updated manifest tokens
    """
    if not cve_id:
        raise Exception("cve_id is required")
    if not package_name:
        raise Exception("package_name is required")
    if not status:
        raise Exception("status is required")

    if scope == "group" and not group_tokens and timesys.llapi.group_token:
        group_tokens = [timesys.llapi.group_token]

    resource = f"/api/v1/vigiles/cves/{cve_id}/vuln-status"
    data = {
        "scope": scope,
        "package": package_name,
        "status": status,
    }

    if justification:
        data["justification"] = justification

    if package_version:
        data["package_version"] = package_version

    if justification_detail:
        data["justification_detail"] = justification_detail

    if manifest_tokens:
        data["manifest_tokens"] = manifest_tokens

    if group_tokens:
        data["group_tokens"] = group_tokens

    return timesys.llapi.POST(resource, data_dict=data)


def get_vuln_status(
    cve_id: str,
    package_name: str,
    package_version: str,
    manifest_token: str,
):
    """Get Status for a vulnerability reported against SBOM

    Parameters
    ----------
    cve_id : str
        CVE ID for vulnerability status
    package_name : str
        Name of the package for which the vulnerability status is requested
    package_version : str
        Version of the package for which the vulnerability status is requested
    manifest_token : str
        SBOM token

    Returns
    -------
    dict
        Vulnerability status data against SBOM
    """
    if not cve_id:
        raise Exception("cve_id is required")

    if not package_name:
        raise Exception("package_name is required")

    if not package_version:
        raise Exception("package_version is required")

    if not manifest_token:
        raise Exception("manifest_token is required")

    data = {
        "manifest_token": manifest_token,
        "package_name": package_name,
        "package_version": package_version
    }

    resource = f"/api/v1/vigiles/cves/{cve_id}/vuln-status"
    return timesys.llapi.GET(resource, data_dict=data)
