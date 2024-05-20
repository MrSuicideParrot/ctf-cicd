"""
Copy from ctfcli
"""

from urllib.parse import urljoin

from requests import Session


class APISession(Session):
    def __init__(self, *args, prefix_url: str = "", verify_tls: bool = True, **kwargs):
        super(APISession, self).__init__(*args, **kwargs)
        # Strip out ending slashes and append a singular one so we generate
        # clean base URLs for both main deployments and subdir deployments
        self.prefix_url: str = prefix_url.rstrip("/") + "/"
        self.verify: bool = verify_tls

    def request(self, method: str, url: str, *args, **kwargs):
        # Strip out the preceding / so that urljoin creates the right url
        # considering the appended / on the prefix_url
        url = urljoin(self.prefix_url, url.lstrip("/"))
        return super(APISession, self).request(method, url, *args, **kwargs)
