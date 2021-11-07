import getpass
import json

from urllib.parse import urlencode
from urllib.request import Request, urlopen

def input_credentials():
    username = input("Enter username/email for Pushsafer: ")
    key = getpass.getpass("Enter API key for Pushsafer: ")
    return username, key

def validate_key(username, key):
    url = 'https://www.pushsafer.com/api-k'
    post_fields = {
        "u" : username,
        "k" : key,
        }
    request = Request(url, urlencode(post_fields).encode())
    status = json.loads(urlopen(request).read().decode())
    return status['status']


def notify(key, device, url, message):
    url = 'https://www.pushsafer.com/api'
    post_fields = {
        "d" : device,
        "t" : 'Campsite Availability Update',
        "m" : message,
        "s" : 11,
        "v" : 3,
        "i" : 33,
        "c" : '#FF0000',
        "u" : url,
        "ut" : 'Campground Page',
        "k" : key,
    }

    request = Request(url, urlencode(post_fields).encode())
    status = json.loads(urlopen(request).read().decode())
    return status['status']

    

