import os
import subprocess
from typing import List, Optional

from .api import APISession
import logging as log


class Config:
    _config: Optional['Config'] = None

    def __init__(self, verify_tls: bool = True) -> None:
        self.access_token: Optional[str] = os.getenv(
            "CTFD_TOKEN", default=None)
        self.url: Optional[str] = os.getenv("CTFD_URL", default=None)
        self.verify_tls: bool = verify_tls

        if not self.access_token or not self.url:
            raise ValueError(
                "CTFD_TOKEN and CTFD_URL environment variables must be set")

        self.docker_compose_name: List[str] = self._find_docker_compose()

    def _find_docker_compose(self) -> List[str]:
        docker_compose_name: List[str] = []
        status, _ = subprocess.getstatusoutput("docker-compose -v")

        if status == 0:
            docker_compose_name = ["docker-compose"]
        else:
            status, _ = subprocess.getstatusoutput("docker compose")
            if status == 0:
                docker_compose_name = ["docker", "compose"]
            else:
                log.fatal("Docker-compose binary not found! Unable to run!")
                raise EnvironmentError(
                    "Unable to find docker-compose binary. Please install it on this machine.")

        return docker_compose_name

    @staticmethod
    def generate_config(verify_tls: bool) -> 'Config':
        if Config._config is None:
            Config._config = Config(verify_tls=verify_tls)
        return Config._config

    @staticmethod
    def generate_session() -> APISession:
        if Config._config is None:
            raise Exception("Config was not initialized!")

        # This check is redundant, its just to make the linter happy
        if Config._config.url is None:
            raise ValueError("CTFD_URL must be set")

        s = APISession(prefix_url=Config._config.url,
                       verify_tls=Config._config.verify_tls)
        s.headers.update(
            {"Authorization": f"Token {Config._config.access_token}"})
        return s

    @staticmethod
    def get_docker_compose_command() -> List[str]:
        if Config._config is None:
            raise Exception("Config was not initialized!")

        return Config._config.docker_compose_name
