echo "I am in this directory."
pwd
cd /root/turkey
python3 get_ip.py
python spoof.py
echo "file should transfer. see for error below"
ls /root/MDA_DNS_INPUT/
echo 'see above files and then below'
cat transfer_to_us_blocked_domains_with_ns.txt >> /root/MDA_DNS_INPUT/

ls /root/MDA_DNS_INPUT/
