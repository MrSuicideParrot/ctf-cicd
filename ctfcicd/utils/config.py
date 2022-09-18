import os
from .api import APISession



class Config:

    _config = None

    def __init__(self, verify_tls=True) -> None:
        self.access_token = os.getenv("CTFD_TOKEN", default=None)
        self.url = os.getenv("CTFD_URL", default=None)
        self.verify_tls = verify_tls

    @staticmethod
    def generate_config(verify_tls:bool):
        if Config._config == None:
            Config._config = Config(verify_tls=verify_tls)
        return Config._config


    @staticmethod
    def generate_session():
        if Config._config == None:
            raise Exception("Config was not initialized!")

        s = APISession(prefix_url= Config._config.url, verify_tls= Config._config.verify_tls)
        s.headers.update({"Authorization": f"Token { Config._config.access_token}"})
        return s
