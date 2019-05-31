echo "I am in this directory."
pwd
echo 'just deleted old directory'
cd /root/temp_country
echo 'spoofing script about to start'
python spoof.py
echo 'all spoofed packets sent'
cat transfer_to_us_blocked_domains_with_ns.txt >> /root/MDA_DNS_INPUT/transfer_to_us_blocked_domains_with_ns.txt

