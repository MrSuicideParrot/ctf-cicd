import re


def sanitize_name(name):
    return re.sub(r'\W+', '', name.lower().replace(" ", "_"))
