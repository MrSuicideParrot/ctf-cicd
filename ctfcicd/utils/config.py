import os

from .api import APISession


def generate_session():
    access_token = os.getenv("CTFD_TOKEN", default=None)
    url = os.getenv("CTFD_URL", default=None)

    if not access_token or not url:
        raise Exception("CTFD_TOKEN or CTFD_URL not defined in the environment variables")

    s = APISession(prefix_url=url)
    s.headers.update({"Authorization": f"Token {access_token}"})
    return s
