#! /usr/bin/env python3

"""Find out the IP address of the computer running this command"""

import requests

IP_REST_API = 'https://api.ipify.org'


def get_your_IP():
    """Return the source IP address of the host running the script (in string)."""
    try:
        data = requests.get(IP_REST_API)
        source_ip = data.text.strip()
    except Exception as ex:
        source_ip = "NOTFOUND: " + str(type(ex)) + ": " + str(ex)
    return source_ip


if __name__ == "__main__":
    print(get_your_IP())
