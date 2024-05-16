import re


def sanitize_name(name: str) -> str:
    return re.sub(r'\W+', '', name.lower().replace(" ", "_"))
