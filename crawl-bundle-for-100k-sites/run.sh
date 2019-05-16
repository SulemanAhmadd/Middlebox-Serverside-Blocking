date
mkdir PAK_yourcity
python3 collection/load_webpages_threaded.py requests 30 top-10k-sites.txt PAK_yourcity/
python3 summarize/summarize_csv.py PAK_yourcity
tar -cf PAK_yourcity.tar.gz PAK_yourcity
date
