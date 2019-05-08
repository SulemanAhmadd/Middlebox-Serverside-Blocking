bash set_bind_server_up.sh
country=$( cat /root/country.txt )
python3 ./step1_resolve_here/my_bind.py
cat step1_resolve_here/*fail* | awk '{print$1}' > step1_resolve_here/$country"_blocked_domains.txt"
cat step1_resolve_here/*success* > $country"_resolved_domains.txt"
sshpass -p "&AYB&&D#H8#@" scp -o StrictHostKeyChecking=no ./$country"_resolved_domains.txt" root@108.62.49.40:/root/ACTIVE_DOMAIN_SET/
rm step1_resolve_here/*success*
rm step1_resolve_here/*fail*


