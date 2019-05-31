#! /usr/bin/env python3

"""Parse a list of webpages"""

import sys
import re


def remove_protocol_stuff(url):
    """Remove http:// like stuff

    >>> remove_protocol_stuff('www.x.com/hi')
    'www.x.com/hi'

    >>> remove_protocol_stuff('http://www.x.com')
    'www.x.com'

    >>> remove_protocol_stuff('https://www.x.com')
    'www.x.com'

    >>> remove_protocol_stuff('HTTP://www.x.com')
    'www.x.com'
    """
    if re.match('^http://', url, re.IGNORECASE):
        return url[7:]
    if re.match('^https://', url, re.IGNORECASE):
        return url[8:]
    return url


def normalize_url(url):
    """ Normalize a URL

    >>> normalize_url("www.gap.com")
    'www.gap.com/'

    >>> normalize_url("www.Gap.com/")
    'www.gap.com/'

    >>> normalize_url("www.Gap.com/new")
    'www.gap.com/new'

    >>> normalize_url("hTtps://www.Gap.com/new")
    'www.gap.com/new'

    >>> normalize_url("hTtps://www.Gap.com/New")
    'www.gap.com/New'
    """
    address = remove_protocol_stuff(url)
    parts = address.split('/')
    domain_name = parts[0]
    domain_name = domain_name.lower()
    file_path_parts = parts[1:]
    ### Used this code to manually check that no two paths are same
    ### except for capitalization
    # for p in file_path_parts:
    #    if p != p.lower():
    #        # print("capitalized file path", url)
    #        # raise Exception("capitalized file path", url)
    rest = "/".join(parts[1:])
    return domain_name + "/" + rest


def parse_file(webpage_url_list_file_name):
    """Given the name of file with on URL per line, return those URLs as a list"""
    try:
        webpage_urls = []
        with open(webpage_url_list_file_name,'r') as webFile:
            for line in webFile:
                entry = line.strip()
                if entry[0] != "#": # lines starting # are comments
                    # to throw away "1. " from lists like "1. google.com":
                    ind = line.find(' ')
                    if(ind != -1):
                        entry = line[:ind]
                    webpage_urls.append(entry)
        # print(str(len(webpage_urls)) + " domains were found\n")
        return webpage_urls
    except Exception as ex:
        print("Parsing webpage URL list.  Input file name not working: ",
              webpage_url_list_file_name)
        raise ex


def parse_file_normalize(webpage_url_list_file_name):
    """Given the name of file with on URL per line, return those URLs as a list"""
    return [normalize_url(url) for url in parse_file(webpage_url_list_file_name)]
