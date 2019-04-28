country=$( cat /root/country.txt )
replace_string="s/pakistan/$country/g"
find ./ -type f -exec sed -i -e $replace_string {} \;
echo -e 'eUbGc8ICNA'| sudo -S apt-get install sshpass -y
echo -r 'eUbGc8ICNA'| sudo apt-get install expect -y 
cp -r /root/dns/ ./step1_resolve_here
cp -r /root/dns/ ./step3_resolve_again_get_ns
python3 ./step1_resolve_here/my_bind.py
cat step1_resolve_here/*fail* | awk '{print$1}' > step2_present_in_us_not_here/blocked_domains.txt
cat step1_resolve_here/*fail* | awk '{print$1}' > step1_resolve_here/blocked_domains.txt
cat step1_resolve_here/*success* > step1_resolve_here/resolved_domains.txt
rm step1_resolve_here/*success*
rm step1_resolve_here/*fail*
python ./step2_present_in_us_not_here/get_server_side_blocked.py
cp ./step2_present_in_us_not_here/server_side_blocked.txt step3_resolve_again_get_ns/server_side_blocked.txt
python3 ./step3_resolve_again_get_ns/get_nameservers.py
cat ./step3_resolve_again_get_ns/*blocked_domain_ns_info.txt* > ./step3_resolve_again_get_ns/blocked_domain_ns_info.txt
cat ./step3_resolve_again_get_ns/*domains_resolved* > ./step3_resolve_again_get_ns/domains_resolved
cat ./step3_resolve_again_get_ns/*last_response_received.txt* > ./step3_resolve_again_get_ns/last_response_received.txt
rm ./step3_resolve_again_get_ns/*trac*
cat ./step3_resolve_again_get_ns/blocked_domain_ns_info.txt | awk '{if($1!=""&& $1!="root" && $2=="")print$1" "$6}' > ./step_6_fill_table/ip_of_ns_not_available.txt
cat ./step3_resolve_again_get_ns/blocked_domain_ns_info.txt | awk '{if($2!=""&& $1!="root")print$1" "$6}' >./step4_traceroute/blocked_domains_with_ns.txt
cat ./step3_resolve_again_get_ns/blocked_domain_ns_info.txt | awk '{if($2!=""&& $1!="root")print$1}' >./step4_traceroute/blocked_domains_list.txt
cat ./step3_resolve_again_get_ns/blocked_domain_ns_info.txt | awk '{if($2!=""&& $1!="root")print$6}' >./step4_traceroute/blocked_ip_list.txt
sudo zmap --probe-module=icmp_echoscan --whitelist-file=./step4_traceroute/blocked_ip_list.txt -o ./step4_traceroute/1_icmp_test.txt
sudo zmap --probe-module=icmp_echoscan --whitelist-file=./step4_traceroute/blocked_ip_list.txt -o ./step4_traceroute/2_icmp_test.txt
sudo zmap --probe-module=icmp_echoscan --whitelist-file=./step4_traceroute/blocked_ip_list.txt -o ./step4_traceroute/3_icmp_test.txt
cat ./step4_traceroute/*_icmp_test* > ./step4_traceroute/icmp_reachable_auth_server_ips
cat ./step4_traceroute/*_icmp_test* > ./step_6_fill_table/icmp_reachable_auth_server_ips
rm ./step4_traceroute/*_icmp_test*
echo -e 'eUbGc8ICNA'| sudo -S python ./step4_traceroute/collect_traceroute.py blocked_domains_with_ns.txt &

echo "hey collect_traceroute already started" 
cat ./step3_resolve_again_get_ns/blocked_domain_ns_info.txt | awk '{if($2!=""&& $1!="root")print$1" "$6}' >./step5_run_in_us/transfer_to_us_blocked_domains_with_ns.txt
cat ./step4_traceroute/blocked_domains_with_ns.txt |awk '{print$2}'| uniq| awk '{print"tracelb -d 53 -P udp-sport "$1}' > ./step5_run_in_us/run.txt
dig +retry=5 +short myip.opendns.com @resolver1.opendns.com > ./step5_run_in_us/send_spoofed_packet_here.txt
# suleman this is where automation part starts. line 38 open tcpdump in test country. line 39 transfer a folder in US. line 40 runs a script in that folder in US
echo -e 'eUbGc8ICNA'|sudo -S timeout 300 tcpdump src 108.62.49.40 -w spoof_capture.pcap &
expect test.exp 
cat run_in_us.sh| sshpass -p "&AYB&&D#H8#@" ssh -o StrictHostKeyChecking=no root@108.62.49.40 &
echo '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'

# this is the end of part which needs automation
 
