# SPDX-FileCopyrightText: 2023 Timesys Corporation
# SPDX-License-Identifier: MIT

import timesys

from typing import List, Optional

def get_groups():
    """Get group info for all active groups available to the current user

    Returns
    -------
    list of dict containing
        name : str
            Group name
        description : str
            Group description
        token : str
            Group token
        group_type : str
            Group type (Group or Subgroup)
        organization_token : str
            Parent organization token
    """

    resource = "/api/v1/vigiles/groups"
    return timesys.llapi.GET(resource)


def get_archived_groups():
    """Get group info for all archived groups available to the current user

    Returns
    -------
    list of dict containing
        name : str
            Group name
        description : str
            Group description
        token : str
            Group token
        group_type : str
            Group type (Group or Subgroup)
        organization_token : str
            Parent organization token
    """

    resource = "/api/v1/vigiles/groups/archived"
    return timesys.llapi.GET(resource)


def create_group(group_name, group_description=None, group_token=None):
    """Create a new group for the current user

    Parameters
    ----------
    group_name : str
        Name for the new group
    group_description : str, optional
        Description for the new group
    group_token: str, optional
        If group to be created is a subgroup, provide group token of parent
        group


    Returns
    -------
    dict
        name : str
            Name of group
        description : str
            Description of group
        token : str
            Token of the new group
    """

    if not group_name:
        raise Exception("group_name is required")

    resource = "/api/v1/vigiles/groups"
    data = {"group_name": group_name}

    if group_description:
        data["description"] = group_description

    if group_token is None:
        group_token = timesys.llapi.group_token

    if group_token:
        data["group_token"] = group_token

    return timesys.llapi.POST(resource, data_dict=data)


def get_group_info(group_token=None, subgroups=False):
    """Get group information from a group_token

    If a token is passed, it will be used.
    If no token is passed, but a group_token is configured on the llapi object, it will be used.
    If neither are provided, an Exception will be raised.

    Parameters
    ----------
    group_token : str, optional
        Token of the group to retrieve info for
    subgroups: bool, optional
        Set this to True to include subgroup details, default is False

    Returns
    -------
    dict
        name : str
            Group name
        description : str
            Group description
        token : str
            Group token
        group_type : str
            Group type (Group or Subgroup)
        organization_token : str
            Parent organization token
        subgroups : dict
            Subgroup dict containing subgroup name and token
    """

    if group_token is None:
        group_token = timesys.llapi.group_token

    if not group_token:
        raise Exception('group_token is required either as a parameter or configured on the llapi object')

    resource = f"/api/v1/vigiles/groups/{group_token}"
    data = {"subgroups": subgroups}

    return timesys.llapi.GET(resource, data_dict=data)


def bulk_archive_groups(tokens: List[str]):
    """Mark multiple groups as archived

    Parameters
    ----------
    tokens : List[str]
        List of group tokens to mark as archived
    """

    data = {"tokens": tokens}

    resource = "/api/v1/vigiles/groups/archive"
    return timesys.llapi.PATCH(resource, data_dict=data)


def bulk_unarchive_groups(tokens: List[str]):
    """Mark multiple groups as unarchived

    Parameters
    ----------
    tokens : List[str]
        List of group tokens to mark as unarchived
    """

    data = {"tokens": tokens}

    resource = "/api/v1/vigiles/groups/unarchive"
    return timesys.llapi.PATCH(resource, data_dict=data)


def delete_group(group_token):
    """Deletes a given group/subgroup

    Parameters
    ----------
    group_token : str
        Token of the group to be deleted

    Raises
    ------
    Exception
        If no group_token is provided

    Returns
    -------
    dict
        message: str
            Success message on successful deletion
        status_code: int
            Status code
    """
    if not group_token:
        raise Exception('group_token is required')

    resource = f"/api/v1/vigiles/groups/{group_token}"

    return timesys.llapi.DELETE(resource)


def get_group_members(group_token):
    """Gets a list of group members

    Parameters
    ----------
    group_token : str
        Token of the group whose members are to be retrieved

    Raises
    ------
    Exception
        If no group_token is provided

    Returns
    -------
    dict
        group_name : str
            Name of the group
        description : str
            Description of the group
        token : str
            Group token
        group_type : str
            Type of the group
        group_members : list of dict
            An array of objects, representing a group member's details
    """
    if not group_token:
        raise Exception('group_token is required')

    resource = f"/api/v1/vigiles/groups/{group_token}/members"

    return timesys.llapi.GET(resource)


def add_group_member(group_token, member_email, role, access_subgroups=False):
    """Adds a new member to the specified group.

    Parameters
    ----------
    group_token : str
        Token of the group to which the member is to be added
    member_email : str
        Email address of the member to be added
    role : str
        Role to assign to the new member
    access_subgroups : bool, optional
        If True, user will be allowed access to all the subgroups of the specified group

    Raises
    ------
    Exception
        If any of the required parameters (`group_token`, `member_email`, or `role`) is not provided

    Returns
    -------
    dict
        message: str
            Success message on successfuly adding the user
        status_code: int
            Status code
    """
    if not group_token:
        raise Exception('group_token is required')
    if not member_email:
        raise Exception('member_email is required')
    if not role:
        raise Exception('role is required')

    resource = f"/api/v1/vigiles/groups/{group_token}/members"
    payload = {
        "member_email": member_email,
        "role": role,
        "allow_access_to_subgroups": access_subgroups
    }

    return timesys.llapi.POST(resource, data_dict=payload, json=True)


def update_group_member(group_token, member_email, new_role):
    """Update the group member

    Parameters
    ----------
    group_token : str
        Token of the group to which the member is to be updated
    member_email : str
        Email address of the member to be updated
    new_role : str
        New role to assign to the member

    Returns
    -------
    dict
        message: str
            Success message on successfuly adding the user
        status_code: int
            Status code

    Raises
    ------
    Exception
        If any of the required parameters (`group_token`, `member_email`, or `role`) is not provided.
    """
    if not group_token:
        raise Exception('group_token is required')
    if not member_email:
        raise Exception('member_email is required')
    if not new_role:
        raise Exception('new_role is required')

    resource = f"/api/v1/vigiles/groups/{group_token}/members/{member_email}"
    payload = {
        "new_role": new_role
    }

    return timesys.llapi.PUT(resource, data_dict=payload, json=True)

def remove_group_member(group_token, member_email):
    """Remove a user from the specified group

    Parameters
    ----------
    group_token : str
        Token of the group from which the user is to be removed
    member_email : str
        Email Address of the user to be removed from the group

    Returns
    -------
    dict
        message: str
            Success message on successfuly adding the user
        status_code: int
            Status code

    Raises
    ------
    Exception
        If any of the required parameters (`group_token`, `member_email`) is not provided.
    """
    if not group_token:
        raise Exception('group_token is required')
    if not member_email:
        raise Exception('member_email is required')

    resource = f"/api/v1/vigiles/groups/{group_token}/members/{member_email}"

    return timesys.llapi.DELETE(resource)


def get_group_settings(group_token=None):
    """Get group settings for a group

    If a token is passed, it will be used.
    If no token is passed, but a group_token is configured on the llapi object, it will be used.
    If neither are provided, an Exception will be raised.

    Parameters
    ----------
    group_token : str, optional
        Token of the group to retrieve group settings info for

    Returns
    -------
    dict
        name : str
            Group name
        token : str
            Group token
        "vuln_identifiers": List
            List of identifiers used to match the vulnerabilities
        "vuln_strict_match": str
            "on" if strict vulnerability based on name and vendor is enabled else "off"
    """

    if group_token is None:
        group_token = timesys.llapi.group_token

    if not group_token:
        raise Exception('group_token is required either as a parameter or configured on the llapi object')

    resource = f"/api/v1/vigiles/groups/{group_token}/settings"

    return timesys.llapi.GET(resource)


def update_group_settings(group_token=None, vuln_identifiers=None, vuln_strict_match=None):
    """Update group settings for a group

    If a token is passed, it will be used.
    If no token is passed, but a group_token is configured on the llapi object, it will be used.
    If neither are provided, an Exception will be raised.

    Parameters
    ----------
    group_token : str, optional
        Token of the group to retrieve group settings info for
    vuln_identifiers: List, Optional
        List of identifiers used to match the vulnerabilities
    vuln_strict_match: str, Optional
        "on" if strict vulnerability based on name and vendor is enabled else "off"

    Returns
    -------
    dict
        message: str
            Success message on successfuly updating the group settings
        status_code: int
            Status code
    """

    if group_token is None:
        group_token = timesys.llapi.group_token

    if not group_token:
        raise Exception('group_token is required either as a parameter or configured on the llapi object')

    resource = f"/api/v1/vigiles/groups/{group_token}/settings"

    payload = {}

    if vuln_identifiers is not None:
        payload["vuln_identifiers"] = vuln_identifiers
    if vuln_strict_match is not None:
        payload["vuln_strict_match"] = vuln_strict_match

    return timesys.llapi.PATCH(resource, data_dict=payload)