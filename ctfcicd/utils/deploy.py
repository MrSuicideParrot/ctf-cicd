import logging as log
import os
from pathlib import Path

from docker import from_env

from images import sanitize_name


def ssh(challenge, host, network: None):
    os.environ["DOCKER_HOST"] = host
    client = from_env(use_ssh_client=True)

    path = Path(challenge.file_path).parent.absolute()

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
        exposed_ports[i] = i

    client.containers.run(image=image_name, name=container_name, restart_policy="unless-stopped",
                          exposed_ports=exposed_ports, network=network, detach=True)
    log.info("Container update with success")

    """
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=f"_{str(image_name)}.docker.tar")
    for chunk in image.save():
        temp.write(chunk)
    temp.close()

    ssh_host.send_file(temp.name)
    temp.delete
    ssh_host.close()
    """


DEPLOY_HANDLERS = {"ssh": ssh}
