mkdir ./process_parser/anomaly
mkdir ./process_parser/traces
mkdir ./process_parser/complete_stitched_paths
mkdir ./process_parser/unreached
apt-get install sshpass -y
#sshpass -p "&AYB&&D#H8#@" scp -o StrictHostKeyChecking=no root@108.62.49.40:/root/MDA_DNS_INPUT/have_auth_no_ip_extended.common_three_runs.txt .
sleep 3
sshpass -p "&AYB&&D#H8#@" scp -o StrictHostKeyChecking=no root@108.62.49.40:/root/DNS_SCAMPER/scamper .
echo "stage 1"
python find_commands.py
echo "stage 2"
number_of_sites=$( cat have_auth_no_ip_extended.common_three_runs.txt | wc -l )
time="$((number_of_sites*100))"
echo "stage 3"
sudo timeout $time tcpdump icmp or udp -w MDA_DNS_tcpdump_logs.pcap &
echo "stage 4"
sudo ./scamper -o MDA_DNS_scamper_output.txt -O cmdfile -f scamper_commands.txt
echo "Congrats! Data collection completed!"
