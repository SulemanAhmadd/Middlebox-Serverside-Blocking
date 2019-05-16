all:
	echo "Nothing to make.  Just for cleaning and testing."

test: clean
	python3 -m doctest webpage_list_parser.py
	printf "www.google.com\nwww.cnn.com\nbestbuy.com\nthis.is.not.a.real.dns.name.akdjfadf\n240.0.0.0\n127.0.0.1\nwww.worldjournal.com/page-privacy-policy/\n" > test-urls.txt
	python3 load_webpages.py requests 3 test-urls.txt loads-test-out

clean:
	rm -f *~
	rm -rf __pycache__/
	rm -rf loads-test-out/
	rm test-urls.txt
