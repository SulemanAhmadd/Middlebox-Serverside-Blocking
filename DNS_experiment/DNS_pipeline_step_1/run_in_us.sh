echo "I am in this directory."
pwd
rm -rf /root/temp_country
echo 'just deleted old directory'
cd /root/temp_country
python3 get_ip.py
python spoof.py
echo "file should transfer. see for error below"
ls /root/MDA_DNS_INPUT/
echo 'see above files and then below'
cat transfer_to_us_blocked_domains_with_ns.txt >> /root/MDA_DNS_INPUT/transfer_to_us_blocked_domains_with_ns.txt

ls /root/MDA_DNS_INPUT/
