import os
import re
import logging as log

from ctfcicd.utils.deploy import DEPLOY_HANDLERS
from utils.challenge import load_installed_challenges, load_challenge, Yaml, sync_challenge, create_challenge
from urllib.parse import urlparse


class CiCd:
    def __init__(self):
        self.deploy_uri = os.getenv("DEPLOY_HOST", default=None)
        log.info("CTFcli initialized")

    def check_if_challenge_exists(self, challenge: Yaml) -> bool:
        installed_challenges = load_installed_challenges()
        for c in installed_challenges:
            if c["name"] == challenge["name"]:
                return True

        return False

    # Synchronize all challenges in the given category, where each challenge is in it's own folder.
    def sync_folder(self, category):
        local_challenges = [f"{category}/{name}" for name in os.listdir(f"./{category}") if
                            os.path.isdir(f"{category}/{name}")]

        installed_challenges = load_installed_challenges()

        for challenge in local_challenges:
            if os.path.exists(f"{challenge}/challenge.yml"):
                log.info(f"Checking challenge: {challenge}")
                try:
                    chall_class = load_challenge(f"{challenge}/challenge.yml")
                except Exception as e:
                    log.warning(f"Error loading challenge {challenge}/challenge.yml - ", e)
                    continue

                if self.check_if_challenge_exists(chall_class):
                    log.info(f"Synchronising {challenge}/challenge.yml")
                    sync_challenge(chall_class)
                else:
                    log.info(f"Installing {challenge}/challenge.yml")
                    create_challenge(chall_class)

                if chall_class.get("image") is not None:
                    target_host = chall_class.get("host") or self.deploy_uri
                    if bool(target_host) is False:
                        log.warning("This challenge can't be deployed because there is no target host to deploy to.")
                        continue

                    url = urlparse(target_host)
                    if bool(url.netloc) is False:
                        log.warning("Provided host has no URI scheme. Provide a URI scheme like ssh:// or registry://")

                    try:
                        status, domain, port = DEPLOY_HANDLERS[url.scheme](
                            challenge=chall_class, host=target_host
                        )
                    except Exception as e:
                        log.warning("Error while deploying challenge - ", e)
                        continue

                    if status:
                        log.info(f"Challenge deployed at {domain}:{port}")
                    else:
                        log.warning(f"An error occured during deployment")

    def deploy_current_folder(self):
        for i in self.get_categories():
            log.info("Synchronizing " + i + "challenges")
            self.sync_folder(i)

    # Each category is in it's own directory, get the names of all directories that do not begin with '.'.
    @staticmethod
    def get_categories():
        denylist_regex = r'\..*'

        categories = [name for name in os.listdir(".") if
                      os.path.isdir(name) and not re.match(denylist_regex, name)]
        log.info("Categories: " + ", ".join(categories))
        return categories
