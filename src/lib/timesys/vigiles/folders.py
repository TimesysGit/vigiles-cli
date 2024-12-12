# SPDX-FileCopyrightText: 2022 Timesys Corporation
# SPDX-License-Identifier: MIT

import timesys


def get_folders(product_token=None, folder_token=None):
    """**Access to this route requires a Vigiles prime subscription..**

    Get all folders that are owned by the current user.

    If a product token is configured on the llapi object, only folders belonging
    to that product will be returned.

    If a folder token is configured on the llapi object, only folders belonging
    to that folder will be returned.

    Returns
    -------
    list of dict
        List of folder information dictionaries with keys:
            "folder_token", "folder_name", "folder_description", "creation_date", "product_token"
    """

    data = {}
    product_token = product_token or timesys.llapi.product_token
    folder_token = folder_token or timesys.llapi.folder_token

    if product_token and not folder_token:
        data["product_token"] = product_token
    if folder_token:
        data["folder_token"] = folder_token

    resource = "/api/v1/vigiles/folders"
    return timesys.llapi.GET(resource, data_dict=data)
