# Let's collect input for MDA DNS and then transfer MDA DNS list to each
# VP
python do_all_EC2_and_one_provider_VPS.py 5

# As each VP has list we can start MDA DNS now

python do_all_EC2_and_one_provider_VPS.py 6

# Once MDA DNS is complete we can use MODE 7 to start path stitching
# and MODE 8 to get data back.
