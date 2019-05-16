#! /usr/bin/env python3

"""To run the code, run the following in terminal:

  python3 load_webpage.py [selenium|requests] timeoutVal urlList [directory]

"""

import sys
import json
import load_webpage
import os
import errno
import webpage_list_parser


def run_tests(driver_name, timeout, webpage_urls):
    results = []
    for webpage_url in webpage_urls:
        result_dict = load_webpage.run_test(driver_name, timeout, webpage_url)
        results.append(result_dict)
    return(results)


def main(argv):
    if len(argv) not in [4, 5]:
        print("Incorrect number of arguments: ", str(argv))
        print(__doc__)
        sys.exit(2)

    driver = argv[1]
    # Verifying selected driver method
    if driver not in ['requests', 'selenium']:
        print("Invalid driver selected: ", str(driver))
        print(__doc__)
        sys.exit(2)

    timeout = int(argv[2])
    webpage_url_list_file_name = argv[3]
    webpage_urls = webpage_list_parser.parse_file(webpage_url_list_file_name)

    directory_name = argv[4]
    # This code has to deal with a race condition:
    #   if not os.path.exists(directory):
    # So, use a try-catch instead
    try:
        os.makedirs(directory_name)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    for webpage_url in webpage_urls:
        out_file_name = directory_name + "/result_" + webpage_url.replace('/','-').replace(':','-') + ".json"
        load_webpage.main(["load_webpages.py",
                           driver,
                           str(timeout),
                           webpage_url,
                           out_file_name])

# Clean but less robust:
#     result_dict_list = run_tests(driver, timeout, webpage_urls)
# 
#     result_str = json.dumps(result_dict_list, indent=4)
# 
#     if len(argv) == 4:
#         print(result_str)
#     else:
#         output_file_name = argv[4]
#         with open(output_file_name, 'w') as out_fh:
#             out_fh.write(result_str)
#             out_fh.write("\n")

if __name__ == "__main__":
    main(sys.argv)
