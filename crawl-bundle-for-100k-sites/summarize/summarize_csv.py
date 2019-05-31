#! /usr/bin/env python3

"""Call with python summarize.py <result_dir>

This produces a great deal of output to std out, but that is just for
debugging.  The actual output is in a CSV file with the name
  ```<result_dir>-all.csv```
The CSV has the following header:
  ```URL, Experiment status, Experiment blocktype, Response Size```
where

 - URL is the website that the experiment attempted to load

 - Experiment status is the status code returned when attempting to
   load the URL.  If no code exists because the page failed to load
   before getting one, a code showing the type of error is provided
   instead.

 - Experiment blocktype is the category code for the type of blocking,
   or just the status code (again) if no blocking is found.

 - Response size, the size of the response's body (sometimes a block
   page)
"""

import json
import os
import sys
import shutil

import categorize


def summarize(results_dir_name):
    """Summarize the results in results_dir_name

    Produces a CSV file as the main output.  What's printed to std out
    is just for debugging progress, and a quick and dirty summary.
    """
    status_200s = 0
    status_403s = 0
    geoblocks = 0
    abuseblocks = 0
    both = 0
    try:
        shutil.rmtree('geoblocked-htmls')
    except:
        pass
    try:
        shutil.rmtree('abuseblocked-htmls')
    except:
        pass
    os.makedirs('geoblocked-htmls')
    os.makedirs('abuseblocked-htmls')
    results_dir = os.listdir(results_dir_name)
    results_summary = {} # stores an overview all the result files
    out = open(results_dir_name.replace('/', '-')+'all.csv', 'w')
    # OLD Way:  out.write('URL, Experiment status, Experiment blocktype, Response Size\n')
    out.write('URL, Status code, Blocktype, Response size\n')
    for afile in results_dir:
        if not afile.endswith('.json'):
            continue

        # Each file holds the results of a single load attempt in
        # JSON.  Parse it into a dict.
        try:
            load_result = json.load(open(os.path.join(results_dir_name, afile)))
        except:
            continue

        url = load_result['url']

        if load_result['response_received?']:
            t_status = load_result['status_code']
            if t_status == 403:
                status_403s += 1
            t_headers = load_result['headers']
            t_content = load_result['body']
            t_block, t_blocktype = categorize.response(t_status, t_headers, t_content)
            if t_block == False:
                if t_status == 200:
                    status_200s += 1
            if ":GEO_BLOCKED" in t_blocktype:
                geoblocks += 1
                with open(os.path.join('geoblocked-htmls', url.replace('/','-')+'.html'), 'w') as obj:
                    obj.write(t_content)
            if ":ABUSE_BLOCKED" in t_blocktype:
                abuseblocks += 1
                with open(os.path.join('abuseblocked-htmls', url.replace('/','-')+'.html'), 'w') as obj:
                    obj.write(t_content)
            if "$BOTH$" in t_blocktype:
                both += 1
                # with open(os.path.join('geoblocked-htmls', url+'.html'), 'w') as obj:
                #     obj.write(t_content)

        else:
            t_content = load_result['body']
            t_status = categorize.error_name(t_content)
            t_blocktype = ''

        # Record the length for use in the length heuristic:
        t_size = len(t_content)

        # Write out the row for the CSV file:
        out.write(url + ',\"' + str(t_status) +  '\",'+ str(t_blocktype)+ ',' + str(t_size) + '\n')

        # Record some information for the summary
        if t_status in results_summary:
             results_summary[t_status].append(url+'--'+t_blocktype)
        else:
             results_summary[t_status] = [url+'--'+t_blocktype]

    print('200 nonblocks- ' + str(status_200s))
    print('403 all - ' + str(status_403s))
    print('Geo_blocks - ' + str(geoblocks))
    print('Abuse_blocks - ' + str(abuseblocks))
    print('Both - ' + str(both))
    # The rest of this function is just for the std out summary information
    # print('********** Summary *********\n')
    #
    # for aval in results_summary:
    #     print(aval, len(results_summary[aval]))
    # print('********** Detail *********\n')
    # for aval in results_summary:
    #     if aval == 200:
    #         continue
    #     print(str(aval) + ':')
    #     for ares in results_summary[aval]:
    #           print(ares)


if __name__== '__main__':

    if len(sys.argv) != 2:
        print('Not the right number of enough arguments.' +
        'Correct command for creating summary: python summarize.py results_dir.\n Exiting ...')
        sys.exit(2)

    results_dir_name = sys.argv[1]
    summarize(results_dir_name)
