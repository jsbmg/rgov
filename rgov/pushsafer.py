import getpass
import json
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from rgov import locations


def input_credentials() -> tuple[str, str]:
    """Prompt for Pushsafer API credentials."""
    user = input("Enter username/email for Pushsafer: ")
    key = getpass.getpass("Enter API key for Pushsafer: ")
    return user, key


def write_credentials(email, key, passcmd=False):
    """ Write Pushsafer credentials to disk with 600 permissions."""
    os.makedirs(os.path.join(locations.CONFIG_DIR, "rgov"), exist_ok=True)
    os.umask(0)
    if passcmd:
        print("Not yet implemented.")
    with open(
        os.open(locations.AUTH_FILE, os.O_CREAT | os.O_WRONLY, 0o600), "w"
    ) as file:
        file.truncate(0)
        file.write(f"{email}\n")
        file.write(f"{key}")


def read_credentials():
    """Read stored Pushsafer credentials from disk."""
    with open(locations.AUTH_FILE, "r") as file:
        content = file.readlines()
        content = [line.strip() for line in content]
        user = content[0]
        key = content[1]
        return user, key


def validate_key(user: str, key: str) -> bool:
    """Return whether the Pushsafer credentials are valid or not."""
    url = "https://www.pushsafer.com/api-k"
    fields = {"u": user, "k": key}
    req = Request(url, urlencode(fields).encode())
    status = json.loads(urlopen(req).read().decode())
    if status["status"] == 1:
        return True
    else:
        return False


def gen_notifier_text(cg_availability: dict) -> str:
    msg = ""
    for name, sites in cg_availability.items():
        n_sites = len(sites)
        available = ", ".join(sites)
        if 0 < n_sites < 10:
            msg += f"{name}: site(s) {available} available!\n"
        elif n_sites > 10:
            n_sites = len(sites)
            msg += f"{name}: {n_sites} sites available!\n"
    return msg


def notify(key: str, device: str, msg: str, url=None) -> dict:
    endpoint = "https://www.pushsafer.com/api"
    post_fields = {
        "d": device,
        "t": "Campsite Availability Update",
        "m": msg,
        "s": 11,
        "v": 3,
        "i": 33,
        "c": "#FF0000",
        "k": key,
    }
    if url:
        post_fields["u"] = url
        post_fields["ut"] = "Campsite Page"

    req = Request(endpoint, urlencode(post_fields).encode())
    status = json.loads(urlopen(req).read().decode())
    return status
