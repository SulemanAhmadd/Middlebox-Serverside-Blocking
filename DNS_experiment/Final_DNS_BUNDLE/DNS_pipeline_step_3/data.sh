cp MDA_DNS_scamper_output.txt ./process_parser/
cp transfer_to_us_blocked_domains_with_ns.txt ./process_parser/
cp MDA_DNS_tcpdump_logs.pcap ./process_parser/
python ./process_parser/get_tashark_logs.py
python ./process_parser/parse_scamper.py
country=$( cat /root/country.txt )
cat ./process_parser/complete_stitched_paths/final_log > $country"_final_log"
sshpass -p "&AYB&&D#H8#@" scp -o StrictHostKeyChecking=no ./$country"_final_log" root@108.62.49.40:/root/GLOBAL_MDA_DNS_LOGS/
