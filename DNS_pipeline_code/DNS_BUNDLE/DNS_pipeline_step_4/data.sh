tr -d '\000' < MDA_DNS_scamper_output.txt > ./process_parser/MDA_DNS_scamper_output.txt
cp ./process_parser/MDA_DNS_scamper_output.txt .
#cp MDA_DNS_scamper_output.txt ./process_parser/
cp have_auth_no_ip_extended.common_three_runs.txt ./process_parser/
cp MDA_DNS_tcpdump_logs.pcap ./process_parser/
echo "We are now going to extract pcap trace for each website from large pcap trace." >> progress_logs.txt
python ./process_parser/get_tashark_logs.py
echo "We have traces now. Time to start path stitching process." >> progress_logs.txt
python ./process_parser/parse_scamper.py
country=$( cat /root/country.txt )
cat ./process_parser/complete_stitched_paths/final_log > $country"_final_log"
