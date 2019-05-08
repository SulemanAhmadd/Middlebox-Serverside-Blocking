sshpass -p "&AYB&&D#H8#@" scp -o StrictHostKeyChecking=no root@108.62.49.40:/root/ACTIVE_DOMAIN_SET/active_domains.txt ./step2_resolve_again_get_ns/
cat ./step2_resolve_again_get_ns/active_domains.txt | awk '{print$1}' >./step2_resolve_again_get_ns/active_domains_set.txt
python3 ./step2_resolve_again_get_ns/get_nameservers.py
cat ./step2_resolve_again_get_ns/*blocked_domain_ns_info.txt* > ./step2_resolve_again_get_ns/blocked_domain_ns_info.txt
cat ./step2_resolve_again_get_ns/*domains_resolved* > ./step2_resolve_again_get_ns/domains_resolved
cat ./step2_resolve_again_get_ns/*last_response_received.txt* > ./step2_resolve_again_get_ns/last_response_received.txt
rm ./step2_resolve_again_get_ns/*trac*

