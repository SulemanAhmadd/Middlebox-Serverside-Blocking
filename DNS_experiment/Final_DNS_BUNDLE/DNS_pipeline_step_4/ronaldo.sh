country=$( cat /root/country.txt )
replace_string="s/temp_country/$country/g"
find ./ -type f -exec sed -i -e $replace_string {} \;
echo -e 'eUbGc8ICNA'| sudo -S apt-get install sshpass -y
echo -r 'eUbGc8ICNA'| sudo apt-get install expect -y 
cat ./step3_resolve_again_get_ns/have_auth_no_ip_extended.common_three_runs.txt | awk '{if($1!="")print}' >./step3_resolve_again_get_ns/blocked_domain_ns_info.txt
echo '*************************************************'
cat ./step3_resolve_again_get_ns/blocked_domain_ns_info.txt | awk '{print$3" "$2}' >./step5_run_in_us/transfer_to_us_blocked_domains_with_ns.txt

dig +retry=5 +short myip.opendns.com @resolver1.opendns.com > ./step5_run_in_us/send_spoofed_packet_here.txt

number_of_sites=$( cat ./step5_run_in_us/transfer_to_us_blocked_domains_with_ns.txt | wc -l )
time="$((number_of_sites*10))"
echo -e 'eUbGc8ICNA'|sudo -S timeout $time tcpdump udp port 43246 -w spoof_capture.pcap &
expect test.exp 
cat run_in_us.sh| sshpass -p "enterpr2se" ssh -o StrictHostKeyChecking=no root@85.209.163.15 &
echo 'Congrats!'

# this is the end of part which needs automation
 
