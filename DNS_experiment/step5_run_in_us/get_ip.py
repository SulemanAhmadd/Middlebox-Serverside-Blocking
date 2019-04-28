import sys
sys.path.insert(0, '/root')
from dns import resolver


with open("send_spoofed_packet_here.txt",'r') as file:
	external_ip = file.read()


#array of tuples with domain, NS, IP
domains=[]
with open("transfer_to_us_blocked_domains_with_ns.txt",'r') as file:
	domains_raw=file.read().split("\n")


res = resolver.Resolver()
res.nameservers = ['127.0.0.1']
for one_domain in domains_raw:
	separate=one_domain.split(" ")
	if len(separate)>1:
		try:
			answers = res.query(separate[0])

			for rdata in answers:
			#	print (rdata.address)
				domains.append((separate[0],separate[1],str(rdata)))
				with open("domain_ns_ip.txt",'a') as file:
					file.write(separate[0]+" "+separate[1]+" "+str(rdata)+"\n")
				break
		except:
			pass

print(domains)