import logging as log
import os
import subprocess
from pathlib import Path

from docker import from_env

from .images import sanitize_name


def ssh(challenge, host, network="bridge"):
    os.environ["DOCKER_HOST"] = host

    if os.path.exists(f"{challenge}/docker-compose.yml"):
        log.info("Deploying docker-compose")
        subprocess.run(["docker-compose", "-f", f"{challenge}/docker-compose.yml", "up", "-d"], check=True)
        log.info("Docker-compose deployed correctly.")
        return None

    else:
        client = from_env(use_ssh_client=True)

        path = str(Path(challenge.file_path).parent.absolute())

        image_name = sanitize_name(challenge.get("image"))
        container_name = image_name + "_cont"

        image, _ = client.images.build(path=path, tag=image_name)

        cont = client.containers.list(filters={'name': container_name}, sparse=True)

        assert len(cont) <= 1

        if len(cont) == 1:
            if cont[0].image.id != image.id:
                """ Remove container """
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

        exposed_ports = {}
        for i in ports:
            exposed_ports[i] = i.split("/")[0]

        client.containers.run(image=image_name, name=container_name, restart_policy={"Name": "unless-stopped"},
                              ports=exposed_ports, network=network, detach=True)
        log.info("Container update with success")

        return list(exposed_ports.values())[0]


DEPLOY_HANDLERS = {"ssh": ssh}
