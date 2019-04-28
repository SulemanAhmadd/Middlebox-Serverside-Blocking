cp /root/DNS_SCAMPER/scamper .
cp /root/MDA_DNS_INPUT/transfer_to_us_blocked_domains_with_ns.txt .
python find_commands.py
number_of_sites=$( cat transfer_to_us_blocked_domains_with_ns.txt | wc -l )
time="$((number_of_sites*3))"
sudo timeout $time tcpdump icmp or udp -w MDA_DNS_tcpdump_logs.pcap &
sudo ./scamper -o MDA_DNS_scamper_output.txt -O cmdfile -f scamper_commands.txt