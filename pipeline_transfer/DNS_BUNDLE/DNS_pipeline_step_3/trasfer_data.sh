number_of_sites=$( cat ./step5_run_in_us/transfer_to_us_blocked_domains_with_ns.txt | wc -l )
time="$((number_of_sites*15))"
screen -m -d bash -c "date >> tcpdump_logs;sudo timeout $time tcpdump udp and src port 53 and dst port 43246 -w actual_spoof_capture.pcap; date >> tcpdump_logs"
echo "We are now going to transfer spoofing folder for actual spoofed packets" >> ../DNS_pipeline_step_1/progress_logs.txt





# Before transfering step5_run_in_us folder to remote machine, we remove old data by following command
script -q -c "ssh -i ~/.ssh/stardust-lums -o StrictHostKeyChecking=no root@162.244.80.77 'rm -rf ~/temp_country; ls; pwd ; ls | grep temp_country'" > ssh_logs1
#Now tranfering the step5_run_in_us folder
script -q -c "scp -i ~/.ssh/stardust-lums -pr -o StrictHostKeyChecking=no ./step5_run_in_us root@162.244.80.77:/root/temp_country" > ssh_logs2
echo "Spoofing folder transferred and now actual spoofing script about to be started" >> ../DNS_pipeline_step_1/progress_logs.txt
#expect test.exp 
# Now we are asking the remote machine to start sending fake spoofed packets

script -q -c "ssh -i ~/.ssh/stardust-lums -o StrictHostKeyChecking=no root@162.244.80.77 'cd ~/temp_country; pwd;ls;python spoof.py;pwd > temp_country.txt;'" > ssh_logs3

echo "Actual spoofing script started" >> ../DNS_pipeline_step_1/progress_logs.txt
