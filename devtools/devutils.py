import os
from distutils.util import strtobool


def envvartobool(var: str, on_unclear: bool = False) -> bool:
    try:
        return bool(strtobool(os.getenv(var, "0")))
    except ValueError:
        return on_unclear
