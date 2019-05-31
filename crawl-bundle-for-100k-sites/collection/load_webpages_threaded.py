#! /usr/bin/env python3

"""To run the code, run the following in terminal:

  python3 load_webpages_threaded.py [selenium|requests] timeoutVal urlList output_directory [speed]

"""

import sys
import json
import load_webpage
import os
import errno
import webpage_list_parser
import threading


def getpages(driver, timeout, webpage_urls, directory_name):
    for webpage_url in webpage_urls:
        webpage_url = webpage_url
        # out_file_name = directory_name + "/result_" + webpage_url.replace('/','-').replace(':','-') + ".json"
        load_webpage.main(["load_webpages.py",
                           driver,
                           str(timeout),
                           webpage_url,
                           directory_name])


def run(driver_name, timeout, webpage_urls, directory_name, speed):
	
	tlist = []
	for i in range(0, len(webpage_urls), speed):
		t = threading.Thread(target = getpages,
                                     args = (driver_name, timeout, webpage_urls[i:i+speed], directory_name))
		t.daemon = True
		tlist.append(t)
		t.start()

	for athread in tlist:
		athread.join()


def main(argv):
    """ argv has the form
    load_webpages_threaded.py [selenium|requests] timeoutVal urlList output_directory [speed]"""
    if len(argv) not in [5, 6]:
        print("Incorrect number of arguments.")
        print(__doc__)
        sys.exit(2)

    driver = argv[1]
    # Verifying selected driver method
    if driver not in ['requests', 'selenium']:
        print("Invalid driver selected.")
        print(__doc__)
        sys.exit(2)

    timeout = int(argv[2])

    webpage_list_file_name = argv[3]
    webpage_urls = webpage_list_parser.parse_file(webpage_list_file_name)

    # This code has to deal with a race condition:
    #   if not os.path.exists(directory):
    # So, use a try-catch instead
    directory_name = argv[4]
    try:
        os.makedirs(directory_name)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    # Default to using chunks of size 200.  100 got us errors.  Larger
    # numbers are slower.
    speed = 400
    if len(argv) > 5:
          speed = int(argv[5])

    run(driver, timeout, webpage_urls, directory_name, speed)

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
