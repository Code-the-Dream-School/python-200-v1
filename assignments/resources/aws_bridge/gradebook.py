"""A stand-in for the Code the Dream gradebook API.

This file is provided for the Practicum AWS Bridge. Do not change it.
A real version would send an HTTP request with the token. This version
checks the token and reads the bundled submissions.json file instead.
"""

import json
from pathlib import Path

DATA_FILE = Path(__file__).parent / "submissions.json"


class GradebookAuthError(Exception):
    """Raised when the gradebook token is missing."""


def fetch_submissions(token):
    """Return the cohort's roster and submissions as a dictionary."""
    if not token:
        raise GradebookAuthError("A gradebook token is required.")
    with open(DATA_FILE) as f:
        return json.load(f)
