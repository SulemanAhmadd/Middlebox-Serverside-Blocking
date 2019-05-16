Code for doing the crawling and collecting the results 

This code has to be shipped to vantages.

`load_webpage.py` contains the code for attempting to access a
webpage.  See its docstring for how to run it.  In short:
```
python3 load_webpage.py driver timeout url [file]
```
where driver is `requests` or `selenium`.  It will produce a Json
record holding the results of the attempt.  The optional `file` input
is a file name for storing the results instead of having them go to
the terminal.

`load_webpages.py` is similar:
```
python3 load_webpages.py driver timeout urlsfile [directory]
```
except that it takes a urlsfile holding many URLs, one per line, and
an optional directory to for the results files.  It always produces
output files, each named after the URL tested.

`yourip.py` tells you what your IP address is.  Run with
`python3 yourip.py`.
