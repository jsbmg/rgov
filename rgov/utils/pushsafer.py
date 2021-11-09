import getpass
import json

from urllib.parse import urlencode
from urllib.request import Request, urlopen

def input_credentials() -> tuple[str, str]:
    username = input("Enter username/email for Pushsafer: ")
    key = getpass.getpass("Enter API key for Pushsafer: ")
    return username, key

def validate_key(username: str, key: str) -> bool:
    url = 'https://www.pushsafer.com/api-k'
    post_fields = {
        "u" : username,
        "k" : key,
        }
    request = Request(url, urlencode(post_fields).encode())
    status = json.loads(urlopen(request).read().decode())
    if status['status'] == 1:
        return True
    else:
        return False

def gen_notifier_text(campground_results: dict) -> str:
    message = ""
    for name, available in campground_results.items():
        num_sites = len(available)
        available_str = ", ".join(available)
        if 0 < num_sites < 10:
            message += f"{name}: site(s) {available_str} available!\n"
        elif num_sites > 10:
            message += f"{name}: {num_sites} sites available!\n"
        else:
            continue
    return message


def notify(key: str, device:str, message: str, url=None) -> dict:
    endpoint = 'https://www.pushsafer.com/api'
    post_fields = {
        "d" : device,
        "t" : 'Campsite Availability Update',
        "m" : message,
        "s" : 11,
        "v" : 3,
        "i" : 33,
        "c" : '#FF0000',
        "k" : key,
    }
    if url:
        post_fields['u'] = url
        post_fields['ut'] = 'Campsite Page'

    request = Request(endpoint, urlencode(post_fields).encode())
    status = json.loads(urlopen(request).read().decode())
    return status
