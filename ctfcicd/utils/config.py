import os
from .api import APISession
import logging as log
import subprocess

class Config:

    _config = None

    def __init__(self, verify_tls=True) -> None:
        self.access_token = os.getenv("CTFD_TOKEN", default=None)
        self.url = os.getenv("CTFD_URL", default=None)
        self.verify_tls = verify_tls

        status, result = subprocess.getstatusoutput("docker-compose -v")
        if status == 0:
            self.docker_compose_name = ["docker-compose"]
        else:
            status, result = subprocess.getstatusoutput("docker compose")
            if status == 0:
                self.docker_compose_name = ["docker", "compose"]
            else:
                log.fatal("Docker-compose binary not found! Unable to run!")
                raise Exception("Unable to find docker-compose binary. Please install it on this machine.")

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
        s.headers.update({"Authorization": f"Token {Config._config.access_token}"})
        return s

    @staticmethod
    def get_docker_compose_command():
        if Config._config == None:
            raise Exception("Config was not initialized!")
        
        return Config._config.docker_compose_name