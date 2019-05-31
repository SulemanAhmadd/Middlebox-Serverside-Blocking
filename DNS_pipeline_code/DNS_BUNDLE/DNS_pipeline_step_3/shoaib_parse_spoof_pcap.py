
from scapy.all import *


packets = rdpcap("spoof_capture.pcap")
spoofed_domains=[]
for packet in packets:
	if packet.proto==17:
		print packet.payload.payload.payload.show()
		print packet.payload.payload.payload.qd.qname
		string_domain=str(packet.payload.payload.payload.qd.qname)
		if string_domain in spoofed_domains:
			continue
		spoofed_domains.append(string_domain)
		with open("./step6_fill_table/received_spoofed_response",'a') as file:
			file.write(string_domain+"\n")
