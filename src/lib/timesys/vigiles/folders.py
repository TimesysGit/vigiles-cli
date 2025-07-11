# SPDX-FileCopyrightText: 2023 Timesys Corporation
# SPDX-License-Identifier: MIT

import timesys


def get_folders(group_token=None, folder_token=None):
    """Get all folders that are owned by the current user.

    If a group token is configured on the llapi object, only folders belonging
    to that group will be returned.

    If a folder token is configured on the llapi object, only folders belonging
    to that folder will be returned.

    Returns
    -------
    list of dict
        List of folder information dictionaries with keys:
            "folder_token", "folder_name", "folder_description", "creation_date", "group_token"
    """

    data = {}
    group_token = group_token or timesys.llapi.group_token
    folder_token = folder_token or timesys.llapi.folder_token

    if group_token and not folder_token:
        data["group_token"] = group_token
    if folder_token:
        data["folder_token"] = folder_token

    resource = "/api/v1/vigiles/folders"
    return timesys.llapi.GET(resource, data_dict=data)


def create_folder(folder_name, description=None, group_token=None, folder_token=None):
    """Create a new folder with given group/folder token

    Returns
    -------
    dict
        Dictionary of new folder information with keys:
            "folder_name", "group_token", "folder_token", "description", "creation_date"
    """

    data = {
        "folder_name": folder_name,
    }
    group_token = group_token or timesys.llapi.group_token
    folder_token = folder_token or timesys.llapi.folder_token

    if description:
        data["description"] = description
    if group_token and not folder_token:
        data["group_token"] = group_token
    if folder_token:
        data["folder_token"] = folder_token

    return timesys.llapi.POST(
        "/api/v1/vigiles/folders",
        data_dict=data
    )
