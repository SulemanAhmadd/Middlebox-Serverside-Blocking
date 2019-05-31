Code for summarizing the results from a single vantage to send to a central analysis point

The results are too large to quickly ship from the vantages to a central place for analyzing it.  So, we just ship summaries made by this code.

This code has to be shipped to vantages.

The file are

- summarize.py creates the summaries.

- categorize.py which categorizes responses so that they (which are vary long since they include the HTML body) can be replaced by a much smaller category code.

- comparestatus.py does what summarize does but to more than one directory full of results at a time.  Currently not used.
