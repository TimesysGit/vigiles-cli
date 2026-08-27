# SPDX-FileCopyrightText: 2026 Timesys Corporation
# SPDX-License-Identifier: MIT

import time

import timesys
from timesys.core.utils import validate_int

JOB_POLL_INTERVAL = 1
JOB_TERMINAL_STATUSES = {"succeeded", "failed"}
DEFAULT_JOB_TIMEOUT = 600


def wait_for_job(job_id, timeout=DEFAULT_JOB_TIMEOUT):
    """ Poll a Vigiles background job until it succeeds, fails, or times out
    """
    if not job_id:
        raise Exception("Vigiles server did not return a job_id")
    if not validate_int(timeout, min=1):
        raise Exception("Job timeout must be a positive integer number of seconds")

    resource = f"/api/v1/vigiles/jobs/{job_id}"
    deadline = time.monotonic() + timeout

    while True:
        result = timesys.llapi.GET(resource)
        status = result.get("status")

        if status in JOB_TERMINAL_STATUSES:
            if status == "failed":
                error = result.get("error") or "Background job failed"
                raise Exception(f"Vigiles job {job_id} failed: {error}") from None
            return result

        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise Exception(f"Timed out waiting for Vigiles job {job_id} after {timeout} seconds") from None

        time.sleep(min(JOB_POLL_INTERVAL, remaining))
