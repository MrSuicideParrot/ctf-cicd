import logging as log
import os
import subprocess
from pathlib import Path
from typing import Optional, Dict

from docker import from_env

from .images import sanitize_name
from .config import Config


def ssh(challenge, host: str, network: str = "bridge") -> Optional[str]:
    os.environ["DOCKER_HOST"] = host

    path = str(Path(challenge.file_path).parent.absolute())
    if os.path.exists(f"{path}/docker-compose.yml"):
        log.info("Deploying docker-compose")
        subprocess.run(Config.get_docker_compose_command(
        ) + ["-f", f"{path}/docker-compose.yml", "build", "--no-cache"], check=False)
        try:
            subprocess.run(Config.get_docker_compose_command(
            ) + ["-f", f"{path}/docker-compose.yml", "down"], check=False)
            subprocess.run(Config.get_docker_compose_command(
            ) + ["-f", f"{path}/docker-compose.yml", "up", "-d"], check=True)
        except Exception as e:
            log.warning(e)
            log.critical("Docker-compose deployed with problem.")
            exit(1)

        log.info("Docker-compose deployed correctly.")
        return None

    else:
        client = from_env(use_ssh_client=True)

        image_name = sanitize_name(challenge.get("image"))
        if image_name == "":
            image_name = sanitize_name(challenge.get("name"))
            if image_name == "":
                log.critical("Unable to build docker image for %s",
                             challenge.get("name"))
                return None

        container_name = image_name + "_cont"

        image, _ = client.images.build(path=path, tag=image_name)

        cont = client.containers.list(
            filters={'name': container_name}, sparse=True)

        assert len(cont) <= 1

        if len(cont) == 1:
            if cont[0].image.id != image.id:
                # Remove container
                cont[0].stop()
                cont[0].remove(v=True, force=True)
            else:
                log.info("It's not necessary to update the container")
                return

        try:
            ports = image.attrs['Config']['ExposedPorts'].keys()
        except KeyError:
            log.warning("Docker image doesn't have exposed ports.")
            return

        exposed_ports: Dict[str, str] = {}
        for i in ports:
            exposed_ports[i] = i.split("/")[0]

        client.containers.run(image=image_name, name=container_name, restart_policy={"Name": "unless-stopped"},
                              ports=exposed_ports, network=network, detach=True)
        log.info("Container update with success")

        return list(exposed_ports.values())[0]


DEPLOY_HANDLERS = {"ssh": ssh}
