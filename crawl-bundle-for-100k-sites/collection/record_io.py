#! /usr/bin/env python3

"""Parse one or more directories full of JSON records"""

import os
import json


def make_file_name(url):
    """converts a URL into something that can be used as a file name

    WARNING: Two URLs can get mapped to the same file name."""
    return url.replace('/','-').replace(':','-') + ".json"


def read_record(file_name):
    """Read a JSON record

    Each file holds the records of a single load attempt in JSON.
    Parse it into a dict.
    """
    with open(file_name, 'r') as url_record_fh:
        url_record = json.load(url_record_fh)
    return url_record


def read_directory(records_dir_name):
    """Read in the JSON records from a single directory holding them

    Returns a hashmap from URLs to dicts representing the record.  The
    file names are not captured.
    """
    recs = {}
    for url_record_fn in os.listdir(records_dir_name):
        if not url_record_fn.endswith('.json'):
            continue
        url_record = read_record(os.path.join(records_dir_name, url_record_fn))
        recs[url_record['url']] = url_record
    return recs


def read_directories(record_dir_names):
    """Read in many directories of JSON records

    Return a hashmap from directory names to hashmaps from URLs to
    record dicts
    """
    recs = {}
    for record_dir_name in record_dir_names:
        recs[record_dir_name] = read_directory(record_dir_name)
    return recs


def read_directory_directory(dir_dir_name):
    ### This alternate code results in the dir_dir_name not being part
    ### of the vantage name:
    recs = {}
    for inner_dir_name in os.listdir(dir_dir_name):
        recs[inner_dir_name] = read_directory(os.path.join(dir_dir_name,inner_dir_name))
    return recs
    ### This code results in having the dir_dir_name name stuck to the front of each vantage dir name:
    # inner_dir_names = os.listdir(dir_dir_name)
    # inner_dir_paths = [os.path.join(dir_dir_name, idn) for idn in inner_dir_names]
    # return read_directories(inner_dir_paths)


def read_directory_directory_directory(dir_dir_dir_name):
    """For example, use way records are stored like this:
    data/study1/USA_LA_VPN/http---www.icsi.berkeley.edu-.json
    Call on "data"."""
    inner_dir_dir_names = os.listdir(dir_dir_dir_name)
    # inner_dir_dir_paths = [os.path.join(dir_dir_dir_name, iddn) for iddn in inner_dir_dir_names]
    result = {}
    for iddn in inner_dir_dir_names:
        inner_dir_dir_path = os.path.join(dir_dir_dir_name, iddn)
        inner_dict = read_directory_directory(inner_dir_dir_path)
        result[iddn] = inner_dict
    return result


def write_record(record, out_dir_name):
    """Assumes the directory already exists"""
    url = record['url']
    output_file_name = make_file_name(url)
    with open(os.path.join(out_dir_name, output_file_name), 'w') as url_out_fh:
        json.dump(record, url_out_fh, indent=4)


def write_directory(records, out_dir_name):
    """Assumes the directory does not exist"""
    try:
        os.makedirs(out_dir_name)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    for url_key in records:
        record = records[url_key]
        write_record(record, out_dir_name)
