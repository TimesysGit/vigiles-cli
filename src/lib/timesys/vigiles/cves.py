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
            "affected_configurations", "assigner", "description", "identifier", "impact", "modified", "problem_types", "published", "references" , "nvd_status", "cisa", "epss"

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
