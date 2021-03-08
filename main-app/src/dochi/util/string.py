import re


def strip_whitespaces(string: str) -> str:
    return re.sub(r"\s+", "", string)
