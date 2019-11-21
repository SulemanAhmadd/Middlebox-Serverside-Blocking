"""

	Run as:
		sudo python3 collect_traceroute.py domain_list_file

	Note: requires root privileges due to scapy

	Also requires disabling the outgoing RSTs. On Linux this can be done as:
		sudo iptables -A OUTPUT -p tcp --tcp-flags ALL RST,ACK -j DROP

"""
import os
import sys
#os.chdir(os.path.dirname(sys.argv[0]))
from multiprocessing import Process
from scapy.all import *
from random import randint
from scapy.layers import *
import threading
import thread
import traceback
import socket
# number of retries for unanswered packets
N_RETRIES = 2
ICMP_REACHABLE_AUTH_SERVERS=[]

def get_ip_list(domain_list):
	domain_ip_list=[]
	for dest in domain_list:
		try:
			if dest=="":
				continue
			dest_IP=socket.gethostbyname(dest)
			one_domain_ip_dictionary=dict()
			one_domain_ip_dictionary["domain"]=dest
			one_domain_ip_dictionary["IP"]=dest_IP
			domain_ip_list.append(one_domain_ip_dictionary)
		except Exception as ex: 
	#		pass #print "!!!!!!!!!!!!!!!! \n\n  ",dest
		#	traceroute_type = get_failing_traceroute(traceback) 
			with open("failed_traceroutes.txt",'a') as f:
				f.write(dest + "\t" + str(type(ex).__name__) + "\tDetails: " +
						str(ex) + "\t" + "icmp" + "\n")            
	return domain_ip_list            
		 

def get_packet_type(packet):
	"""
		Returns the type of received packet
	   
		ICMP:                 ICMP
		TCP-Empty-[flags]:    No payload
		TCP-HTTP-[flags]:     HTTP payload
		TCP-Non_HTTP-[flags]: Non-HTTP payload
	"""
	
	if isinstance(packet.payload, ICMP):
		return "ICMP"
	elif isinstance(packet.payload, UDP):
		if isinstance(packet.payload.payload, DNS):
			return "DNS"
		else:    
			return "UDP"
	elif isinstance(packet.payload, TCP):
		if len(packet.payload[TCP].payload) == 0:
			return "TCP-Empty-" + str(packet.payload[TCP].flags)
		elif "HTTP" in str(packet.payload[TCP].payload).split("\n")[0]: 
			return "TCP-HTTP-" + str(packet.payload[TCP].flags) 
		else:
 
			return "TCP-NonHTTP-" + str(packet.payload[TCP].flags)
	else:
		return "-"


def get_packet_content(packet, packet_type):
	"""
		Returns squeezed TCP payloads 
	"""
	if "TCP" in packet_type:
		packet_content = packet.payload[TCP].payload
		if packet_content:
			squeezed_packet_content = packet_content.strip("\n")
			return squeezed_packet_content
	return str(None)


def has_HTTP_layer(resp_packets):
	for packet in resp_packets:
		# this check is required because an ICMP packet may contain the
		# original HTTP packet, passing the HTTP layer check
		if packet[1].haslayer(ICMP):
			continue
		elif packet[1].haslayer("HTTP"):
			#packet[1].show()
			return True
		else:
			continue
	return False
def get_raw_string(ICMP_ID):
	empty_string="\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
	hex_string=hex(ICMP_ID)
    # pass #print " first half ",hex_string[:4],"  int ",int(hex_string[:4],0)," char ",chr((hex_string[:4]))
	char_1=chr(int(hex_string[:4],0))
 #   temp="0x"+
	char_2=chr(int("0x"+hex_string[4:],0))
	complete_string=char_1+char_2+empty_string
	 
	#pass #print repr(complete_string)
	return (complete_string)

def get_hex_num(ICMP_ID):
	ones_complement=ICMP_ID^0xffff
	without_overflow=ones_complement
	with_overflow=int("0x1"+hex(ones_complement)[2:],0)-1
   # pass #print "- 1",hex(without_overflow)
   # pass #print "- 2",hex(with_overflow)
	answer1=without_overflow-0x0800-ICMP_ID
	answer2=with_overflow-0x0800-ICMP_ID

	#pass #print "answer 1",hex(answer1)
	#pass #print "answer 2",hex(answer2)

	if (answer1>0):
		#pass #print "answer 1",hex(answer1)
		return answer1
	else:
	#	pass #print "answer 2",hex(answer2)
		return answer2
def do_icmp_traceroute(dest,payload):
	"""
		Sends an ICMP echo packet with increasing TTLs
	"""
	"""
		Sends an ICMP echo packet with increasing TTLs
	"""
#	global ICMP_REACHABLE_AUTH_SERVERS
#	if not dest["IP"] in ICMP_REACHABLE_AUTH_SERVERS:
#		return
	token=randint(5000,65535)%256
	payload_number=get_hex_num(token)
	payload_number2=int(payload_number)
	 
   # sys.exit()
	ICMP_SEQ=0
   
	raw_string_arr=["\xdb\x9a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00","\xdb\x99\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00","\xdb\x98\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00","\xdb\x97\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00","\xdb\x96\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00","\xdb\x95\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00","\xdb\x94\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00","\xdb\x93\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00","\xdb\x92\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00","\xdb\x91\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00","\xdb\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00","\xdb\x8f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00","\xdb\x8e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00","\xdb\x8d\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00","\xdb\x8c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00","\xdb\x8b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00","\xdb\x8a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00","\xdb\x89\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00","\xdb\x88\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00","\xdb\x87\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00","\xdb\x86\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00","\xdb\x85\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00","\xdb\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00","\xdb\x83\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00","\xdb\x82\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00","\xdb\x81\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"]
	hex_num=0xdb9a

	IP_ID=256
	counter=0
	out_file = "_".join([payload, "icmptraceroute", ".txt"])
	for ttl in range(1,25):
   #     ans,unans=sr(IP(dst=dest["IP"], ttl=ttl,id=IP_ID)/ICMP(id=ICMP_ID-counter),timeout=20,retry=1)
		raw_string=get_raw_string(payload_number2)
		ans,unans=sr(IP(dst=dest["IP"], ttl=ttl,id=ttl,flags=2)/ICMP(id=token,seq=ICMP_SEQ)/str(raw_string),timeout=20,verbose=0)
		payload_number2=payload_number2-1
		ICMP_SEQ=ICMP_SEQ+1
		with open(out_file, "a") as f:
			pass
			for snd,rcv in ans:
				f.write(str(snd.ttl) + " " + rcv.src + " " + snd.dst + " " + \
						get_packet_type(rcv) + "\n")

	 

def do_tcp_traceroute(dest,payload):
	"""
		Sends a SYN packet with increasing TTLs
	"""
	ans, unans = sr(IP(dst = dest["IP"], 
					   ttl = (1,50),
					   id  = randint(0,10000))/
					TCP(sport = randint(10000,20000), 
						dport = 80, 
						flags = "S"), 
					timeout = 20,
					retry = N_RETRIES)

	out_file = "_".join([payload, "tcptraceroute", ".txt"])
	with open(out_file, "w") as f:
		for snd,rcv in ans:
			f.write(str(snd.ttl) + " " + rcv.src + " " + snd.dst + " " + \
					get_packet_type(rcv) + "\n")


def do_dns_traceroute(dest,payload):
	"""
		Sends a SYN packet with increasing TTLs
	"""
#	ans, unans = sr(IP(dst = dest["IP"], 
#					   ttl = (1,25),
#					   id  = 1)/
#					UDP(sport = 43675, 
#						dport = 53)/
#					DNS(qd=DNSQR(qname=payload)), 
#					timeout = 15,
#					retry = N_RETRIES)

	out_file = "_".join([payload, "dnstraceroute", ".txt"])
#	with open(out_file, "a") as f:
#		for snd,rcv in ans:
#			f.write(str(snd.ttl) + " " + rcv.src + " " + snd.dst + " " + \
#					get_packet_type(rcv) + "\n")
	pass #print "DNS traceroute started for ",dest
	Probe_sport = randint(43675,45700)
	for ttl in range(1,25):
   #     ans,unans=sr(IP(dst=dest["IP"], ttl=ttl,id=IP_ID)/ICMP(id=ICMP_ID-counter),timeout=20,retry=1)
		ans, unans = sr(IP(dst = dest["IP"], 
					   ttl = ttl,
					   id  = ttl)/
					UDP(sport = Probe_sport, 
						dport = 53)/
					DNS(qd=DNSQR(qname=payload)), 
					timeout = 15,
					retry = N_RETRIES,verbose=0)
		with open(out_file, "a") as f:
			pass
			for snd,rcv in ans:
				f.write(str(snd.ttl) + " " + rcv.src + " " + snd.dst + " " + \
						get_packet_type(rcv) + "\n")


def do_http_traceroute_stateless(dest):
	"""
		Sends an HTTP packet with increasing TTLs
	"""
	TCP_ACK = TCP(sport = randint(10000,20000), 
				  dport = 80, 
				  flags = "PA", 
				  seq = randint(20000,80000), 
				  ack = randint(70000,90000))
	HTTP_request_str = "GET / HTTP/1.1\r\nHost: " + dest["domain"] + "\r\nUser-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0\r\nAccept-Language: en-US,en;q=0.5\r\nConnection: keep-alive\r\nUpgrade-Insecure-Requests: 1\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nAccept-Encoding:gzip, deflate\r\n\r\n"
		
	ans, unans = sr(IP(dst = dest["IP"], 
					   ttl = (1,25),
					   id  = randint(0,10000))/
					TCP_ACK/
					HTTP_request_str,
					timeout = 20,
					retry = N_RETRIES)

	out_file = "_".join([dest["domain"], "httptraceroute", "stateless", ".txt"])
	with open(out_file, "w") as f:
		for snd,rcv in ans:
			f.write(str(snd.ttl) + " " + rcv.src + " " + snd.dst + " " + \
					get_packet_type(rcv) + "\n")


def do_http_traceroute_stateful(dest):
	"""
		First establishes a connection with the intended destination, by
		sending a SYN and receiving a SYN-ACK. Then sends an HTTP request with
		increasing TTLs

		Note: Ideally we would just establish the handshake once, and then send
		the HTTP packet with increasing TTLs, but the way we set it up
		currently is because: (i) by the time we get to the last hop, the
		handshake perhaps times out, and (ii) we have not been able to get the
		send-multiple-HTTP-packets-at-once to work.
	"""
	IPL = IP(dst = dest["IP"])
	out_file = "_".join([dest["domain"], "httptraceroute", "stateful", ".txt"])
	response_strings = []
	syn_ack_received_ever = False

	for ttl in range(1, 25):
		source_port = randint(10000,20000)
		TCP_SYN = TCP(sport = source_port, 
					  dport = 80, 
					  flags = "S", 
					  seq = randint(20000,80000))


		'''
			Attempt to get a SYN-ACK from the intended destination
		'''
		N_SYN_ACK_TRIES = 3
		got_syn_ack = False

		for attempt in range(0, N_SYN_ACK_TRIES):
			response = sr1(IPL/TCP_SYN, 
						   timeout = 15)

			if not response or not isinstance(response.payload, TCP): 
				continue
			else:
				if response[TCP].flags == 'SA':
					got_syn_ack = True
					syn_ack_received_ever = True
					TCP_SYNACK = response
				# even if we get a TCP response but it is not SYN-ACK, no need
				# to further proceed -- if it was a case of RST/FIN we should
				# be able to tell it from do_tcp_traceroute
				break
				

		if not got_syn_ack:
			# try the next hop, maybe just a case of packet loss
			# TODO: an overkill at the moment, maybe should give up after a certain
			# threshold
			# continue
			# MJ: commenting out the continue for now, and living with an
			# Exception to avoid the overkill
			raise Exception("No SYN-ACK received")
				

		'''
		Set up the ACK packet with the HTTP request and the correct TTL value"
		'''
		ack_number = TCP_SYNACK.seq + 1
		IP_w_TTL=IP(dst = dest["IP"], ttl=ttl)
		TCP_ACK = TCP(sport = source_port, 
					  dport = 80, 
					  flags = "PA", 
					  seq = TCP_SYN.seq + 1, 
					  ack = ack_number)
		HTTP_request_str = "GET / HTTP/1.1\r\nHost: " + dest["domain"] + "\r\nUser-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0\r\nAccept-Language: en-US,en;q=0.5\r\nConnection: keep-alive\r\nUpgrade-Insecure-Requests: 1\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nAccept-Encoding:gzip, deflate\r\n\r\n"
		HTTP_request = IP_w_TTL/TCP_ACK/HTTP_request_str

		HTTP_response, error = sr(HTTP_request, 
								  timeout = 15, 
								  multi = True,
								  retry = N_RETRIES)


		for snd,rcv in HTTP_response: 
			response_strings.append(str(snd.ttl) + " " + rcv.src + " " +
									snd.dst + " " + get_packet_type(rcv) + "\n")
									#+ " " + get_packet_content(rcv, get_packet_type(rcv)) + "\n")


	if syn_ack_received_ever == False:
		raise Exception("No SYN-ACK received")

	with open(out_file, "w") as f:
		for resp in response_strings:
			f.write(resp)


def get_failing_traceroute(traceback):
	"""
		Parse the traceback and return what traceroute type failed
		TODO: Perhaps there is a better way / place to get the type of failing
		traceroute
	"""
	formatted_lines = traceback.format_exc().splitlines()
	# Get the third line from the traceback
	failing_func_name = formatted_lines[2]
	# Extract traceroute type from strings of the form: " do_icmp_traceroute(dest)"
	failing_type =failing_func_name.split("_")[1]
	return failing_type


def do_all_traceroutes(domain_list,payload_list):
	"""
		Attempt ICMP, TCP, and HTTP traceroutes for the given domain list
	"""
	
	for index in range(len(domain_list)): 
		try:
			 
		#	do_icmp_traceroute(domain_list[index],payload_list[index])
			do_dns_traceroute(domain_list[index],payload_list[index])
		   # pass #print "look at this ",domain_list[index]," ",payload_list[index]
	         
		#    do_http_traceroute_stateless(dest)
		 #   do_http_traceroute_stateful(dest)
		except Exception as ex: 
			traceroute_type = get_failing_traceroute(traceback) 
			with open("failed_traceroutes.txt",'a') as f:
				f.write(domain_list[index]["domain"] + "\t" + str(type(ex).__name__) + "\tDetails: " +
						str(ex) + "\t" + traceroute_type + "\n")
	
def do_all_traceroutes1(domain_list,payload_list):
  #  pass #print "Time to give work to threads work i got ",domain_list
	N_THREADS1 = 2
	children_threads=[]
	THREAD_WORKLOAD1 = max(len(domain_list)/ N_THREADS1, 1)
	for thread_start_index in range(0, len(domain_list), THREAD_WORKLOAD1):
   #     pass #print "-------------"
 		thread_chunk1=domain_list[thread_start_index: thread_start_index + THREAD_WORKLOAD1]
		thread_chunk2=payload_list[thread_start_index: thread_start_index + THREAD_WORKLOAD1]
		pass #print "length of first Thread and second Second\n",len(thread_chunk1),"\n",len(thread_chunk2)
		pass #print(thread_chunk1[0])
		pass #print(thread_chunk2[0])

	 #   pass #print "chunk gone 2 ",thread_chunk1
	  #  pass #print "at this time domain list",domain_list
		child = threading.Thread(target = do_all_traceroutes, 
								 args = (thread_chunk1,thread_chunk2,))
		children_threads.append(child)
		child.start()

	for one_child in children_threads:
		one_child.join()


  #  pass #print " work given above was ",domain_list
	

if __name__ == "__main__":
	domain_list = list()
	N_THREADS = 2
#	global ICMP_REACHABLE_AUTH_SERVERS
#	with open("icmp_reachable_auth_server_ips",'r') as file:
#		ICMP_REACHABLE_AUTH_SERVERS=file.read().split("\n")
	
	 
	with open(sys.argv[1]) as f:
		for line in f:
			domain_list.append(line.strip())
	#pass #print domain_list
	name_server_list=[i.split(" ")[1] for i in domain_list]
	payload_list_list=[i.split(" ")[0] for i in domain_list]

   # pass #print payload_list_list
	 
	domain_ip_list=get_ip_list(name_server_list)
	THREAD_WORKLOAD = max(len(domain_ip_list)/ N_THREADS, 1)
	#pass #print domain_ip_list
	
	'''
	input file 
	abc 1.1.1.1 2.2.2.2
	abc is quesry payload for dns
	1.1.1.1 is nameserver 
	2.2.2.2 is actual ip which we should not have
	'''

	pass #print "length of domain ip list and payload list ",len(domain_ip_list),"\n",len(payload_list_list)

	for i in range(len(domain_ip_list)):
		pass #print domain_ip_list[i]," ",payload_list_list[i]

 
	for thread_start_index in range(0, len(domain_ip_list), THREAD_WORKLOAD):
	#    pass #print thread_start_index, " start ind 1"
		thread_chunk1 = domain_ip_list[thread_start_index: thread_start_index + THREAD_WORKLOAD]
		thread_chunk2 = payload_list_list[thread_start_index: thread_start_index + THREAD_WORKLOAD]
	#	pass #print "length of first chunk and second chunk\n",len(thread_chunk1),"\n",len(thread_chunk2)
   #     pass #print "chunk gone ",thread_chunk
		p = Process(target=do_all_traceroutes1, args=(thread_chunk1,thread_chunk2,))
		p.start()

	
	pass #print "I am done giving work to processes ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"    

	 
	   
