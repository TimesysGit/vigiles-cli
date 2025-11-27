# SPDX-FileCopyrightText: 2023 Timesys Corporation
# SPDX-License-Identifier: MIT

import base64
import gzip

from io import BytesIO

def save_file(data, file_path):
    """Utility function to save 

    Parameters
    ----------
    data : str
        Base64-encoded string representing gzip-compressed file content.
    file_path : str
        Destination path where the file will be saved.
    """
    decoded_data = base64.b64decode(data)

    with gzip.GzipFile(fileobj=BytesIO(decoded_data), mode="rb") as f:
        file_content = f.read()

    with open(file_path, "wb") as report_file:
        report_file.write(file_content)
