import os
import sys
os.chdir(os.path.dirname(sys.argv[0]))
with open("blocked_domains_list.txt",'r') as file:
	domains=file.read().split("\n")


with open("icmp_reachable_auth_server_ips",'r') as file:
	icmp_reachable_auth_server_ips=file.read().split("\n")

for domain in domains:
	if domain=="":
		continue
	icmp_file=domain+"_icmptraceroute_.txt"
	dns_file=domain+"_dnstraceroute_.txt"
	dns_server_found=False
	icmp_server_found=False
	DNS_SERVER_HOP=0
	ICMP_SERVER_HOP=0
	SERVER_IP=""
	try:
		with open(dns_file,"r") as file:
			dns_traceroute=file.read().split("\n")
	except:
		with open("failure.txt",'a') as file:
			file.write(dns_file+"\n")
		continue
	for one_dns_hop in dns_traceroute:
		hop_arr=one_dns_hop.split(" ")
		if len(hop_arr)<4:
			continue
		if domain=="alpariforex.org" or domain=="tamilrockers.to":
			print "!!---------------------------------------------!!"

		print hop_arr," ",domain," ",dns_file
		if hop_arr[3]=="DNS" and hop_arr[1]==hop_arr[2]:
			dns_server_found=True
			DNS_SERVER_HOP=int(hop_arr[0])
			SERVER_IP=hop_arr[2]
			break
	#print dns_traceroute

	if dns_server_found:
		with open("../step6_fill_table/DNS_path_completes",'a') as file:
			file.write(domain+"\n")

		if not SERVER_IP in icmp_reachable_auth_server_ips:
			with open("../step6_fill_table/set1_ip_not_icmp_reachable",'a') as file:
				file.write(domain+"\n")
			continue


		with open(icmp_file,"r") as file:
			icmp_traceroute=file.read().split("\n")
		for one_icmp_hop in icmp_traceroute:
			hop_arr=one_icmp_hop.split(" ")
			if len(hop_arr)<4:
				continue
			print hop_arr
			if hop_arr[3]=="ICMP" and hop_arr[1]==hop_arr[2]:
				icmp_server_found=True
				
				ICMP_SERVER_HOP=int(hop_arr[0])


				break

		if domain=="alpariforex.org"  or domain=="tamilrockers.to":
			print " did icmp server found ",icmp_server_found

		if domain=="alpariforex.org" or domain=="tamilrockers.to":
			print " look at hops"
			print ICMP_SERVER_HOP
			print DNS_SERVER_HOP
		if ICMP_SERVER_HOP-DNS_SERVER_HOP>3:
			with open("../step6_fill_table/set1_middlebox",'a') as file:
				print "yahan aya"
				file.write(domain+"\n")
		else:
			with open("../step6_fill_table/set1_server_side_blocking",'a') as file:
				print "wahan gaya ",domain
				file.write(domain+"\n")

	else:
		with open("../step6_fill_table/DNS_path__does_not_complete",'a') as file:
			file.write(domain+"\n")
