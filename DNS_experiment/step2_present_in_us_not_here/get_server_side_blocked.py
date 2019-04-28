import os
import sys
os.chdir(os.path.dirname(sys.argv[0]))
with open("blocked_domains.txt",'r') as file:
	blocked_domains=file.read().split("\n")

with open("us_available_domains.txt",'r') as file:
	us_domains=file.read().split("\n")

for one_block_domain in blocked_domains:
	for one_us_domain in us_domains:
		if one_block_domain==one_us_domain and one_block_domain!="":
			print one_block_domain
			with open("server_side_blocked.txt",'a') as file:
				file.write(one_block_domain+"\n")
			break
