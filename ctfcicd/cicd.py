import os
from pathlib import PurePath
import re
import logging as log
import subprocess
from urllib.parse import urlparse

from ctfcicd.utils.deploy import DEPLOY_HANDLERS
from ctfcicd.utils.config import Config
from ctfcicd.utils.challenge import load_installed_challenges, load_challenge, Yaml, sync_challenge, create_challenge

log.basicConfig(level=log.INFO)


class CiCd:
    def __init__(self, prod=True, tls_verify=True):
        self.deploy_uri = os.getenv("DEPLOY_HOST", default=None)
        self.deploy_network = os.getenv("DEPLOY_NETWORK", default="bridge")
        self.prod = prod
        Config.generate_config(tls_verify)
        log.info("CTFcli initialized")

    def check_if_challenge_exists(self, challenge: Yaml) -> bool:
        installed_challenges = load_installed_challenges()
        for c in installed_challenges:
            if c["name"] == challenge["name"]:
                return True

        return False

    def deploy_challenge(self, challenge: str) -> None:
        if os.path.exists(f"{challenge}/challenge.yml"):
            log.info("Checking challenge: %s", challenge)

            if self.prod:
                if os.path.exists(f"{challenge}/disabled"):
                    log.info("%s is disabled.", challenge)
                    log.info("%s won't be deployed.", challenge)
                    return

            try:
                chall_class = load_challenge(f"{challenge}/challenge.yml")
            except Exception as e:
                log.warning(
                    "Error loading challenge %s/challenge.yml - %s", challenge, e)
                return

            if self.check_if_challenge_exists(chall_class):
                log.info("Synchronising %s/challenge.yml", challenge)
                sync_challenge(chall_class, ignore=["state"])
            else:
                log.info("Installing %s/challenge.yml", challenge)
                create_challenge(chall_class, [])

            if chall_class.get("image") is not None or os.path.exists(f"{challenge}/docker-compose.yml"):
                target_host = chall_class.get("host") or self.deploy_uri
                if bool(target_host) is False:
                    log.warning(
                        "This challenge can't be deployed because there is no target host to deploy to.")
                    return

                url = urlparse(target_host)
                if bool(url.netloc) is False:
                    log.warning(
                        "Provided host has no URI scheme. Provide a URI scheme like ssh:// or registry://")

                try:
                    port = DEPLOY_HANDLERS[url.scheme](
                        challenge=chall_class, host=target_host, network=self.deploy_network
                    )
                except Exception as e:
                    log.warning("Error while deploying challenge - %s", str(e))
                    exit(1)

                if port is not None:
                    log.info("Challenge %s deployed at %s:%s", challenge,
                             url.netloc[url.netloc.find('@') + 1:], port) # type: ignore

    # Synchronize all challenges in the given category, where each challenge is in it's own folder.
    def sync_folder(self, category: str):
        local_challenges = [f"{category}/{name}" for name in os.listdir(f"./{category}") if
                            os.path.isdir(f"{category}/{name}")]

        for challenge in local_challenges:
            self.deploy_challenge(challenge)

    def sync_folder_with_git(self, github_event, github_sha):
        log.info("Differential syncronise")
        try:
            files = subprocess.check_output(
                ['git', 'diff', '--name-only', github_event, github_sha]).split()
            folders_with_change = list(set([PurePath(
                i.decode()).parents[-3] for i in files if len(PurePath(i.decode()).parents) >= 3]))
            for i in folders_with_change:
                self.deploy_challenge(i.as_posix())
        except subprocess.CalledProcessError as e:
            log.warning("Error running - %s", e)
            self.deploy_current_folder()

    def deploy_current_folder(self):
        for category in self.get_categories():
            log.info("Synchronizing %s challenges", category)
            self.sync_folder(category)

    # Each category is in it's own directory,
    # get the names of all directories that do not begin with '.'.
    @staticmethod
    def get_categories():
        denylist_regex = r"\..*"

        categories = [name for name in os.listdir(".") if
                      os.path.isdir(name) and not re.match(denylist_regex, name)]
        # Fix: Use lazy % formatting in logging function
        log.info("Categories: %s", ", ".join(categories))

        return categories
