# SPDX-FileCopyrightText: 2026 Timesys Corporation
# SPDX-License-Identifier: MIT

import timesys


def get_app_db_version():
    """Get app and vulnerability database version details from Vigiles.

    Returns
    -------
    dict
        app_version : str
            Current Vigiles app version
        database_version : str
            Current vulnerability database version
    """
    resource = "/api/v1/vigiles/about"
    return timesys.llapi.GET(resource)
