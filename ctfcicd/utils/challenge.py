"""
Copy from ctfcli with some adaptations
"""

import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List

import yaml

from .config import Config


class Yaml(dict):
    def __init__(self, data: Dict[str, Any], file_path: str = ""):
        super().__init__(data)
        self.file_path = Path(file_path)
        self.directory = self.file_path.parent


def load_challenge(path: str) -> Yaml:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return Yaml(data=yaml.safe_load(f.read()), file_path=path)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"No challenge.yml was found in {path}") from exc


def load_installed_challenges():
    s = Config.generate_session()
    return s.get("/api/v1/challenges?view=admin", json=True).json()["data"]


def sync_challenge(challenge: Yaml, ignore: List[str]) -> None:
    data: Dict[str, Any] = {
        "name": challenge["name"],
        "category": challenge["category"],
        "description": challenge["description"],
        "type": challenge.get("type", "standard"),
        "value": int(challenge["value"]) if challenge["value"] else challenge["value"],
        **challenge.get("extra", {}),
    }

    # Some challenge types (e.g. dynamic) override value.
    # We can't send it to CTFd because we don't know the current value
    if challenge["value"] is None:
        del challenge["value"]

    if challenge.get("attempts") and "attempts" not in ignore:
        data["max_attempts"] = challenge.get("attempts")

    if challenge.get("connection_info") and "connection_info" not in ignore:
        data["connection_info"] = challenge.get("connection_info")

    installed_challenges = load_installed_challenges()
    for c in installed_challenges:
        if c["name"] == challenge["name"]:
            challenge_id = c["id"]
            break
    else:
        return

    s = Config.generate_session()

    original_challenge = s.get(f"/api/v1/challenges/{challenge_id}", json=data).json()[
        "data"
    ]

    r = s.patch(f"/api/v1/challenges/{challenge_id}", json=data)
    r.raise_for_status()

    # Create new flags
    if challenge.get("flags") and "flags" not in ignore:
        # Delete existing flags
        current_flags = s.get("/api/v1/flags", json=data).json()["data"]
        for flag in current_flags:
            if flag["challenge_id"] == challenge_id:
                flag_id = flag["id"]
                r = s.delete(f"/api/v1/flags/{flag_id}", json=True)
                r.raise_for_status()
        for flag in challenge["flags"]:
            if isinstance(flag, str):
                data = {"content": flag, "type": "static",
                        "challenge_id": challenge_id}
                r = s.post("/api/v1/flags", json=data)
                r.raise_for_status()
            elif isinstance(flag, dict):
                flag["challenge_id"] = challenge_id
                r = s.post("/api/v1/flags", json=flag)
                r.raise_for_status()

    # Update topics
    if challenge.get("topics") and "topics" not in ignore:
        # Delete existing challenge topics
        current_topics = s.get(
            f"/api/v1/challenges/{challenge_id}/topics", json=""
        ).json()["data"]
        for topic in current_topics:
            topic_id = topic["id"]
            r = s.delete(
                f"/api/v1/topics?type=challenge&target_id={topic_id}", json=True
            )
            r.raise_for_status()
        # Add new challenge topics
        for topic in challenge["topics"]:
            r = s.post(
                "/api/v1/topics",
                json={
                    "value": topic,
                    "type": "challenge",
                    "challenge_id": challenge_id,
                },
            )
            r.raise_for_status()

    # Update tags
    if challenge.get("tags") and "tags" not in ignore:
        # Delete existing tags
        current_tags = s.get("/api/v1/tags", json=data).json()["data"]
        for tag in current_tags:
            if tag["challenge_id"] == challenge_id:
                tag_id = tag["id"]
                r = s.delete(f"/api/v1/tags/{tag_id}", json=True)
                r.raise_for_status()
        for tag in challenge["tags"]:
            r = s.post(
                "/api/v1/tags", json={"challenge_id": challenge_id, "value": tag}
            )
            r.raise_for_status()

    # Upload files
    if challenge.get("files") and "files" not in ignore:
        # Delete existing files
        all_current_files = s.get("/api/v1/files?type=challenge", json=data).json()[
            "data"
        ]
        for f in all_current_files:
            for used_file in original_challenge["files"]:
                if f["location"] in used_file:
                    file_id = f["id"]
                    r = s.delete(f"/api/v1/files/{file_id}", json=True)
                    r.raise_for_status()
        files = []
        for f in challenge["files"]:
            file_path = Path(challenge.directory, f)
            if file_path.exists():
                file_object = ("file", file_path.open(mode="rb"))
                files.append(file_object)
            else:
                logging.warning("File %s was not found", file_path)
                raise Exception(f"File {file_path} was not found")

        data = {"challenge_id": challenge_id, "type": "challenge"}
        # Specifically use data= here instead of json= to send multipart/form-data
        r = s.post("/api/v1/files", files=files, data=data)
        r.raise_for_status()

    # Create hints
    if challenge.get("hints") and "hints" not in ignore:
        # Delete existing hints
        current_hints = s.get("/api/v1/hints", json=data).json()["data"]
        for hint in current_hints:
            if hint["challenge_id"] == challenge_id:
                hint_id = hint["id"]
                r = s.delete(f"/api/v1/hints/{hint_id}", json=True)
                r.raise_for_status()

        for hint in challenge["hints"]:
            if isinstance(hint, str):
                data = {"content": hint, "cost": 0,
                        "challenge_id": challenge_id}
            else:
                data = {
                    "content": hint["content"],
                    "cost": hint["cost"],
                    "challenge_id": challenge_id,
                }

            r = s.post("/api/v1/hints", json=data)
            r.raise_for_status()

    # Update requirements
    if challenge.get("requirements") and "requirements" not in ignore:
        installed_challenges = load_installed_challenges()
        required_challenges = []
        for r in challenge["requirements"]:
            if isinstance(r, str):
                for c in installed_challenges:
                    if c["name"] == r:
                        required_challenges.append(c["id"])
            elif isinstance(r, int):
                required_challenges.append(r)

        required_challenges = list(set(required_challenges))
        data = {"requirements": {"prerequisites": required_challenges}}
        r = s.patch(f"/api/v1/challenges/{challenge_id}", json=data)
        r.raise_for_status()

    # Unhide challenge depending upon the value of "state" in spec
    if "state" not in ignore:
        data = {"state": "visible"}
        if challenge.get("state"):
            if challenge["state"] in ["hidden", "visible"]:
                data["state"] = challenge["state"]

        r = s.patch(f"/api/v1/challenges/{challenge_id}", json=data)
        r.raise_for_status()


def create_challenge(challenge: Yaml, ignore: List[str]):
    data = {
        "name": challenge["name"],
        "category": challenge["category"],
        "description": challenge["description"],
        "type": challenge.get("type", "standard"),
        "value": int(challenge["value"]) if challenge["value"] else challenge["value"],
        **challenge.get("extra", {}),
    }

    # Some challenge types (e.g. dynamic) override value.
    # We can't send it to CTFd because we don't know the current value
    if challenge["value"] is None:
        del challenge["value"]

    if challenge.get("attempts") and "attempts" not in ignore:
        data["max_attempts"] = challenge.get("attempts")

    if challenge.get("connection_info") and "connection_info" not in ignore:
        data["connection_info"] = challenge.get("connection_info")

    s = Config.generate_session()

    r = s.post("/api/v1/challenges", json=data)
    r.raise_for_status()

    challenge_data = r.json()
    challenge_id = challenge_data["data"]["id"]

    # Create flags
    if challenge.get("flags") and "flags" not in ignore:
        for flag in challenge["flags"]:
            if isinstance(flag, str):
                data = {"content": flag, "type": "static",
                        "challenge_id": challenge_id}
                r = s.post("/api/v1/flags", json=data)
                r.raise_for_status()
            elif isinstance(flag, dict):
                flag["challenge"] = challenge_id
                r = s.post("/api/v1/flags", json=flag)
                r.raise_for_status()

    # Create topics
    if challenge.get("topics") and "topics" not in ignore:
        for topic in challenge["topics"]:
            r = s.post(
                "/api/v1/topics",
                json={
                    "value": topic,
                    "type": "challenge",
                    "challenge_id": challenge_id,
                },
            )
            r.raise_for_status()

    # Create tags
    if challenge.get("tags") and "tags" not in ignore:
        for tag in challenge["tags"]:
            r = s.post(
                "/api/v1/tags", json={"challenge_id": challenge_id, "value": tag}
            )
            r.raise_for_status()

    # Upload files
    if challenge.get("files") and "files" not in ignore:
        files = []
        for f in challenge["files"]:
            file_path = Path(challenge.directory, f)
            if file_path.exists():
                file_object = ("file", file_path.open(mode="rb"))
                files.append(file_object)
            else:
                logging.warning("File %s was not found", file_path)
                raise Exception(f"File {file_path} was not found")

        data = {"challenge_id": challenge_id, "type": "challenge"}
        # Specifically use data= here instead of json= to send multipart/form-data
        r = s.post("/api/v1/files", files=files, data=data)
        r.raise_for_status()

    # Add hints
    if challenge.get("hints") and "hints" not in ignore:
        for hint in challenge["hints"]:
            if isinstance(hint, str):
                data = {"content": hint, "cost": 0,
                        "challenge_id": challenge_id}
            else:
                data = {
                    "content": hint["content"],
                    "cost": hint["cost"],
                    "challenge_id": challenge_id,
                }

            r = s.post("/api/v1/hints", json=data)
            r.raise_for_status()

    # Add requirements
    if challenge.get("requirements") and "requirements" not in ignore:
        installed_challenges = load_installed_challenges()
        required_challenges = []
        for r in challenge["requirements"]:
            if isinstance(r, str):
                for c in installed_challenges:
                    if c["name"] == r:
                        required_challenges.append(c["id"])
            elif isinstance(r, int):
                required_challenges.append(r)

        required_challenges = list(set(required_challenges))
        data = {"requirements": {"prerequisites": required_challenges}}
        r = s.patch(f"/api/v1/challenges/{challenge_id}", json=data)
        r.raise_for_status()

    # Set challenge state
    if challenge.get("state") and "state" not in ignore:
        data = {"state": "hidden"}
        if challenge["state"] in ["hidden", "visible"]:
            data["state"] = challenge["state"]

        r = s.patch(f"/api/v1/challenges/{challenge_id}", json=data)
        r.raise_for_status()


def lint_challenge(path):
    try:
        challenge = load_challenge(path)
    except yaml.YAMLError as e:
        logging.warning("Error parsing challenge.yml: %s", e)
        exit(1)

    required_fields = ["name", "author", "category", "description", "value"]
    errors = []
    for field in required_fields:
        if field == "value" and challenge.get("type") == "dynamic":
            pass
        else:
            if challenge.get(field) is None:
                errors.append(field)

    if len(errors) > 0:
        print("Missing fields: ", ", ".join(errors))
        exit(1)

    # Check that the image field and Dockerfile match
    if (Path(path).parent / "Dockerfile").is_file() and challenge.get("image") != ".":
        print("Dockerfile exists but image field does not point to it")
        exit(1)

    # Check that Dockerfile exists and is EXPOSE'ing a port
    if challenge.get("image") == ".":
        try:
            dockerfile = (Path(path).parent / "Dockerfile").open().read()
        except FileNotFoundError:
            print("Dockerfile specified in 'image' field but no Dockerfile found")
            exit(1)

        if "EXPOSE" not in dockerfile:
            print("Dockerfile missing EXPOSE")
            exit(1)

        # Check Dockerfile with hadolint
        proc = subprocess.run(
            ["docker", "run", "--rm", "-i", "hadolint/hadolint"],
            input=dockerfile.encode(),
            check=False
        )
        if proc.returncode != 0:
            print("Hadolint found Dockerfile lint issues, please resolve")
            exit(1)

    # Check that all files exists
    files = challenge.get("files", [])
    errored = False
    for f in files:
        fpath = Path(path).parent / f
        if fpath.is_file() is False:
            print(f"File {f} specified but not found at {fpath.absolute()}")
            errored = True
    if errored:
        exit(1)

    exit(0)
