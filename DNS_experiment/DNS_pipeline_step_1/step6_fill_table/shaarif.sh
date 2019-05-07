export LC_ALL=C
pip install seaborn
python parse_tr.py
python dns_tr_parser.py ../final_log ../step4_traceroute/failed_dns_tr.txt
python both_pass.py
