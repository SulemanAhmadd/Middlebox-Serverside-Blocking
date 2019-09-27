cd ./step1_resolve_here
python get_server_side_blocked.py
cd ..
cat ./step1_resolve_here/active_set.txt > ../DNS_pipeline_step_2/step5_run_in_us/active_domains_to_ip_mapping.txt
cat ./step1_resolve_here/active_set.txt > ../DNS_pipeline_step_3/step5_run_in_us/active_domains_to_ip_mapping.txt
python3 ./step3_resolve_again_get_ns/get_nameservers.py
cat ./step3_resolve_again_get_ns/*blocked_domain_ns_info.txt* > ./run1/blocked_domain_ns_info.txt
cat ./step3_resolve_again_get_ns/*domains_resolved* > ./run1/domains_resolved
cat ./step3_resolve_again_get_ns/*last_response_received.txt* > ./run1/last_response_received.txt
rm ./step3_resolve_again_get_ns/*trac*
cat ./run1/blocked_domain_ns_info.txt | awk '{if($1!=""&& $1!="root"&& $1!="The" && $4=="")print$1}' > ./run1/no_auth_no_ip.txt
cat ./run1/blocked_domain_ns_info.txt | awk '{if($4!=""&& $1!="root" && $1!="The")print$1" "$6}' >./run1/have_auth_no_ip.txt
echo "Custom resolver found auth servers for first time. Time to wait for 9 seconds" >> progress_logs.txt
sleep 9

echo "Finding auth servers now 2nd time. Time below show start of second attempt of custom resolver" >> progress_logs.txt
date >> progress_logs.txt
python3 ./step3_resolve_again_get_ns/get_nameservers.py
cat ./step3_resolve_again_get_ns/*blocked_domain_ns_info.txt* > ./run2/blocked_domain_ns_info.txt
cat ./step3_resolve_again_get_ns/*domains_resolved* > ./run2/domains_resolved
cat ./step3_resolve_again_get_ns/*last_response_received.txt* > ./run2/last_response_received.txt
rm ./step3_resolve_again_get_ns/*trac*
cat ./run2/blocked_domain_ns_info.txt | awk '{if($1!=""&& $1!="root"&& $1!="The" && $4=="")print$1}' > ./run2/no_auth_no_ip.txt
cat ./run2/blocked_domain_ns_info.txt | awk '{if($4!=""&& $1!="root" && $1!="The")print$1" "$6}' >./run2/have_auth_no_ip.txt
echo "Custom resolver found auth servers for second time. Time to wait for 300 seconds. Time below shows time taken by second attempt" >> progress_logs.txt
date >> progress_logs.txt
sleep 9

echo "Custom resolver found auth servers for third time" >> progress_logs.txt
python3 ./step3_resolve_again_get_ns/get_nameservers.py
cat ./step3_resolve_again_get_ns/*blocked_domain_ns_info.txt* > ./run3/blocked_domain_ns_info.txt
cat ./step3_resolve_again_get_ns/*domains_resolved* > ./run3/domains_resolved
cat ./step3_resolve_again_get_ns/*last_response_received.txt* > ./run3/last_response_received.txt
rm ./step3_resolve_again_get_ns/*trac*
cat ./run3/blocked_domain_ns_info.txt | awk '{if($1!=""&& $1!="root"&& $1!="The" && $4=="")print$1}' > ./run3/no_auth_no_ip.txt
cat ./run3/blocked_domain_ns_info.txt | awk '{if($4!=""&& $1!="root" && $1!="The")print$1" "$6}' >./run3/have_auth_no_ip.txt
echo "DNS STEP 1 done! Time below show when 3 runs to find auth servers completed">> progress_logs.txt
date >> progress_logs.txt
echo "IP below shows IP of machine when custom resolver finished its work. This info helps check if VPNs were working" >>progress_logs.txt
dig +retry=5 +short myip.opendns.com @resolver1.opendns.com >> progress_logs.txt
python compare_across_three_runs.py
cp have_auth_no_ip_extended.common_three_runs.txt ../DNS_pipeline_step_2/step3_resolve_again_get_ns/
cp have_auth_no_ip_extended.common_three_runs.txt ../DNS_pipeline_step_3/step3_resolve_again_get_ns/
echo "Its time to start step 2 where we will do DNS traceroute and fake spoofing check" >> progress_logs.txt

cd ../DNS_pipeline_step_2/
bash ronaldo.sh 
bash trasfer_data.sh
echo "IP below shows IP of machine when DNS step 2 completed. This info helps check if VPNs were working" >>progress_logs.txt
dig +retry=5 +short myip.opendns.com @resolver1.opendns.com >> progress_logs.txt
echo "Its time to start step 3 where we will do real spoofing check" >> ../DNS_pipeline_step_1/progress_logs.txt
cd ../DNS_pipeline_step_3
bash ronaldo.sh
bash trasfer_data.sh
echo "IP below shows IP of machine when DNS step 3 completed. This info helps check if VPNs were working" >>progress_logs.txt
dig +retry=5 +short myip.opendns.com @resolver1.opendns.com >> progress_logs.txt
echo "All done!" >> ../DNS_pipeline_step_1/progress_logs.txt
