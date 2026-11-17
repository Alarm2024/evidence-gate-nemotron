"""Application configuration (EV-001: hard-coded secret)."""

# BUG EV-001: secret must come from environment, not source control.
API_SECRET = "hardcoded-demo-secret-do-not-ship"


def get_api_secret() -> str:
    return API_SECRET
