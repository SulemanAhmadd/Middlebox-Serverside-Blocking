echo "I am in this directory."
pwd
echo 'just deleted old directory'
cd /root/temp_country
echo 'trying to find IPs of domains for which we are sending spoofed response'
python3 get_ip.py
echo 'spoofing script about to start'
python spoof.py
echo 'all spoofed packets sent'
echo "file should transfer. see for error below"
ls /root/MDA_DNS_INPUT/
echo 'see above files and then below'
cat transfer_to_us_blocked_domains_with_ns.txt >> /root/MDA_DNS_INPUT/transfer_to_us_blocked_domains_with_ns.txt

ls /root/MDA_DNS_INPUT/
