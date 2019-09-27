sudo service bind9 restart
mkdir run1
mkdir run2
mkdir run3
echo 'Resolving domains through BIND server. Time below show when BIND server started domain resolution! ' >> progress_logs.txt
date >> progress_logs.txt
python3 ./step1_resolve_here/my_bind.py
cat step1_resolve_here/*fail* | awk '{print$1}' > step1_resolve_here/blocked_domains.txt
cat step1_resolve_here/*success* > step1_resolve_here/resolved_domains.txt
rm step1_resolve_here/*success*
rm step1_resolve_here/*fail*
echo 'Bind server has categorized domains into resolved and unresolved domains! Time below show time taken by Bind server' >> progress_logs.txt
date >> progress_logs.txt
echo "IP below shows IP of machine when BIND server finished resolution process. This info helps check if VPNs were working" >>progress_logs.txt
dig +retry=5 +short myip.opendns.com @resolver1.opendns.com >> progress_logs.txt
