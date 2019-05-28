country=$( cat /root/country.txt )
replace_string="s/temp_country/$country/g"
find ./ -type f -exec sed -i -e $replace_string {} \;
echo -e 'eUbGc8ICNA'| sudo -S apt-get install sshpass -y
echo -r 'eUbGc8ICNA'| sudo apt-get install expect -y 
cat ./step3_resolve_again_get_ns/have_auth_no_ip_extended.common_three_runs.txt | awk '{if($1!="")print}' >./step3_resolve_again_get_ns/blocked_domain_ns_info.txt







cat ./step3_resolve_again_get_ns/blocked_domain_ns_info.txt | awk '{print$1" "$2}' >./step4_traceroute/blocked_domains_with_ns.txt
cat ./step3_resolve_again_get_ns/blocked_domain_ns_info.txt | awk '{print$3}' >./step4_traceroute/blocked_domains_list.txt
cat ./step3_resolve_again_get_ns/blocked_domain_ns_info.txt | awk '{print$2}' >./step4_traceroute/blocked_ip_list.txt


echo -e 'eUbGc8ICNA'| sudo -S python ./step4_traceroute/collect_traceroute.py blocked_domains_with_ns.txt &

echo "hey collect_traceroute already started" 
echo '*************************************************'
cat ./step3_resolve_again_get_ns/blocked_domain_ns_info.txt | awk '{print$3" "$2}' >./step5_run_in_us/transfer_to_us_blocked_domains_with_ns.txt

dig +retry=5 +short myip.opendns.com @resolver1.opendns.com > ./step5_run_in_us/send_spoofed_packet_here.txt

number_of_sites=$( cat ./step5_run_in_us/transfer_to_us_blocked_domains_with_ns.txt | wc -l )
time="$((number_of_sites*10))"
echo -e 'eUbGc8ICNA'|sudo -S timeout $time tcpdump src 108.62.49.40 and udp -w spoof_capture.pcap &
expect test.exp 
cat run_in_us.sh| sshpass -p "&AYB&&D#H8#@" ssh -o StrictHostKeyChecking=no root@108.62.49.40 &
echo 'Congrats!'

# this is the end of part which needs automation
 
