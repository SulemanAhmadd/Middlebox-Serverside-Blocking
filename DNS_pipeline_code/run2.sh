# Now we will first collect active domain set and then transfer that set to
# each VP
python do_all_EC2_and_one_provider_VPS.py 3

# Time to start DNS traceroute and spoofing checks

python do_all_EC2_and_one_provider_VPS.py 4

# Now we have to wait for a long time until traceroutes complete
# we can only start MDA DNS when there is no other activity going
# on.
