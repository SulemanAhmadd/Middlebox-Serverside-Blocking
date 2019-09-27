mkdir ./process_parser/anomaly
mkdir ./process_parser/traces
mkdir ./process_parser/complete_stitched_paths
mkdir ./process_parser/unreached
sudo apt-get install sshpass -y
#sshpass -p "&AYB&&D#H8#@" scp -o StrictHostKeyChecking=no root@108.62.49.40:/root/MDA_DNS_INPUT/have_auth_no_ip_extended.common_three_runs.txt .
sleep 3
echo "stage 1 : We have downloaded scamper. Time to find commands for scamper. Time below shows when experiment started" >> progress_logs.txt
date >> progress_logs.txt
python find_commands.py
echo "stage 2 : now we calculate time until which TCP-DUMP should keep sniffing." >> progress_logs.txt
number_of_sites=$( cat have_auth_no_ip_extended.common_three_runs.txt | wc -l )
time="$((number_of_sites*55))"
echo "stage 3 : TCP-DUMP starting in background..." >> progress_logs.txt
screen -m -d bash -c "date >> tcpdump_logs;sudo timeout $time tcpdump icmp or udp -w MDA_DNS_tcpdump_logs.pcap; date >> tcpdump_logs"
#sudo timeout $time tcpdump icmp or udp -w MDA_DNS_tcpdump_logs.pcap &
echo "stage 4 : Scamper starts sending probes." >> progress_logs.txt
sudo ./scamper -o MDA_DNS_scamper_output.txt -O cmdfile -f scamper_commands.txt
echo "Congrats! Data collection completed! Time below shows when experiment ended." >> progress_logs.txt
date >> progress_logs.txt
echo "IP below shows IP of machine when DNS step 4 completed. This info helps check if VPNs were working" >>progress_logs.txt
dig +retry=5 +short myip.opendns.com @resolver1.opendns.com >> progress_logs.txt
