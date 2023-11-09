# SPDX-FileCopyrightText: 2023 Timesys Corporation
# SPDX-License-Identifier: MIT

# Timesys recommended SBOM generation tools
VIGILES_SUPPORTED_TOOLS = {
    "syft": {
        "ecosystems": [
            "angular",
            "c",
            "maven",
            "npm",
            "nuget",
            "python",
        ],
        "url": "https://github.com/anchore/syft",
        "ref_only": False,
    },
    "meta-timesys": {
        "ecosystems": [
            "yocto",
        ],
        "url": "https://github.com/TimesysGit/meta-timesys",
        "ref_only": True,
    },
    "vigiles-buildroot": {
        "ecosystems": [
            "buildroot",
        ],
        "url": "https://github.com/TimesysGit/vigiles-buildroot",
        "ref_only": True,
    },
    "vigiles-openwrt": {
        "ecosystems": [
            "openwrt",
        ],
        "url": "https://github.com/TimesysGit/vigiles-openwrt",
        "ref_only": True,
    },
}
