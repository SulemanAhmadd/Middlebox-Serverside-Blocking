# We will first transfer bundle and then use BIND server to resolve
# domains in each VP.

# This command transfer bundles
python do_all_EC2_and_one_provider_VPS.py 1

# This command starts resolution of domains thorugh BIND server
python do_all_EC2_and_one_provider_VPS.py 2

# Now we have to wait for BIND server to resolve all domains. for 100k domains
# we should wait for around 45 minutes. After 45 min, we will start run2.sh
