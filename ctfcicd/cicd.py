import os
import re
import logging as log
import subprocess


class CiCd:
    def __init__(self):
        CTFD_TOKEN = os.getenv("CTFD_TOKEN", default=None)
        CTFD_URL = os.getenv("CTFD_URL", default=None)

        if not CTFD_TOKEN or not CTFD_URL:
            log.error("CTFD_TOKEN or CTFD_URL not defined in the environment variables")
            exit(1)

        self.deploy_uri = os.getenv("DEPLOY_HOST", default=None)

        os.system(f"echo '{CTFD_URL}\n{CTFD_TOKEN}\ny' | ctf init")
        log.info("CTFcli initialize")

    # Synchronize all challenges in the given category, where each challenge is in it's own folder.
    def sync(self, category):
        challenges = [f"{category}/{name}" for name in os.listdir(f"./{category}") if
                      os.path.isdir(f"{category}/{name}")]

        for challenge in challenges:
            if os.path.exists(f"{challenge}/challenge.yml"):
                log.info(f"Syncing challenge: {challenge}")
                subprocess.run(["ctf", "challenge", "sync", challenge])
                subprocess.run(["ctf", "challenge", "install", challenge])
                if self.deploy_uri is not None:
                    subprocess.run(["ctf", "challenge", "deploy", challenge, "--host=%s" % self.deploy_uri ])

    def deploy_current_folder(self):
        for i in self.get_categories():
            log.info("Synchronizing " + i + "challenges")
            self.sync(i)

    # Each category is in it's own directory, get the names of all directories that do not begin with '.'.
    @staticmethod
    def get_categories():
        denylist_regex = r'\..*'

        categories = [name for name in os.listdir(".") if
                      os.path.isdir(name) and not re.match(denylist_regex, name)]
        log.info("Categories: " + ", ".join(categories))
        return categories
