import os
import sys
with open("common_auth_servers.txt",'r') as file:
	domains=file.read().split("\n")

stats={}
stats_dom={}
# stats[0]=[]
# stats[1]=[]
# stats[2]=[]
# stats[3]=[]
# stats[4]=[]


for domain_ip in domains:
	if domain_ip=="":
		continue
	domain=domain_ip.split(" ")[0]
	icmp_file=domain+"_icmptraceroute_.txt"
	dns_file=domain+"_dnstraceroute_.txt"
	print domain
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
	print "here"
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
		

		try:
			with open(icmp_file,"r") as file:
				icmp_traceroute=file.read().split("\n")
		except:
			with open("failure.txt",'a') as file:
				file.write(icmp_file+"\n")
			continue
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
			
			print "yahan aya"
			#file.write(domain+"\n")
		else:
			pass
	else:
		pass
	

	if icmp_server_found:
		print "**********************************************"
		print "DNS_HOP ",DNS_SERVER_HOP
		print "Server_HOP ",ICMP_SERVER_HOP
		difference=ICMP_SERVER_HOP-DNS_SERVER_HOP

		if not difference in stats.keys():
			stats[difference]=[1]
		else:
			stats[difference].append(1)

		if not difference in stats_dom.keys():
			stats_dom[difference]=[domain]
		else:
			stats_dom[difference].append(domain)


total=0
for key in stats.keys():
	print "key ",key," count ",sum(stats[key])
	total=total+sum(stats[key])


print "total ",total
