import os
from tkinter.messagebox import NO

from .api import APISession

_config = None

class Config:

    def __init__(self, verify_tls=True) -> None:
        self.access_token = os.getenv("CTFD_TOKEN", default=None)
        self.url = os.getenv("CTFD_URL", default=None)
        self.verify_tls = verify_tls

    @staticmethod
    def generate_config(verify_tls:bool):
        _config = Config(verify_tls=verify_tls)

    @staticmethod
    def generate_session():
        if _config == None:
            raise Exception("Config was not initialized!")

        s = APISession(prefix_url=_config.url, verify_tls=_config.verify_tls)
        s.headers.update({"Authorization": f"Token {_config.access_token}"})
        return s
