import re
import os
import sys
os.chdir(os.path.dirname(sys.argv[0]))
import sys
from scapy.all import *
#pass #print my_files[0]
def get_last_nodes(dest,dummy_ip_where_packe_drop,original_trace):
		#print "trace : \n",original_trace
		last_nodes_dict={}
		query_id_ttl={}
		query_id=[]
		ttl=[]
		server_flow_array=[]
		server_flow_ttl=[]
		domain=original_trace.split("\n")[0].split("%")[1].strip(" ")
		pass #print "see domain ",domain
	#	pass #print "I am in func ",dummy_ip_where_packe_drop
		with open("./complete_stitched_paths/final_log",'a') as file:
				file.write("MDA DNS - DNS response of server - "+trace+"\n")
	
		file_path="./traces/"+dest+".pcap"
		pass #print "In get_last_nodes function IP of server : ",dest
		pass #print "packet drop ",dummy_ip_where_packe_drop
		packets = rdpcap(file_path)
		past_packet=["",""]
		for packet in packets:
			past_packet[0]=past_packet[1]
			past_packet[1]=packet
			if (packet.proto) == 17:
				source_ip=packet.payload.src
				server_ip=packet.payload
				server_udp=server_ip.payload
				query_id.append(server_udp.payload.id)
				ttl.append(server_ip.ttl)
			#	pass #print server_udp.payload.show()

				'''
				So algorithm here is that we first pick any packet which is a UDP packet as its visible for proto==17 check
				Then we see if the packet was sent by server as its visible in below condition. if thats the case
				we pick server's flow identifier and add it in server flow array.
				'''
				if packet.payload.src in dest:
					 
					
					copy_query_id=list(query_id)
					copy_ttl=list(ttl)
					copy_query_id.reverse()
					copy_ttl.reverse()
					one_flow_set=set()
					 
					one_flow_set.add(server_ip.src)
					one_flow_set.add(server_ip.dst)
	# remember					one_flow_set.add(server_ip.tos)

					 
					one_flow_set.add(server_udp.sport)
					one_flow_set.add(server_udp.dport)
					server_query_id=server_udp.payload.id
					count=0
					for i in copy_query_id:
						if str(server_query_id) in str(i):
						#	pass #print "yay ",copy_ttl[count]
							pass


						#	break
						count=count+1	

				#	pass #print packet.payload.show()
			#		pass #print one_flow_set
					 
					if not one_flow_set in server_flow_array:
						server_flow_array.append(one_flow_set)
						server_flow_ttl.append([])
			#			pass #print server_flow_array.index(one_flow_set)
					'''
					Now as we have server flow, we see one packet behind that if it was a UDP packet, if it was then
					we check if it was the query to which server had responded. we do this by doing id check.
					Then for that particular flow, we keep a ttl field which is minimum
					'''			

					if server_udp.sport==53 and past_packet[0].payload.proto==17 and server_udp.payload.id==past_packet[0].payload.payload.payload.id:
						relevant_index=server_flow_array.index(one_flow_set)
						server_flow_ttl[relevant_index].append(past_packet[0].payload.ttl)
						server_flow_ttl[relevant_index]=[min(server_flow_ttl[relevant_index])]
						 








			if (packet.proto) == 1:
				if packet.payload.src in dummy_ip_where_packe_drop:
					source_ip=packet.payload.src
		#			pass #print "found sth last "
					one_flow_set=set()
					icmp_ip=packet.payload.payload.payload
					if icmp_ip.proto==1:
						continue
					one_flow_set.add(icmp_ip.src)
					one_flow_set.add(icmp_ip.dst)
# remember				#	one_flow_set.add(icmp_ip.tos)

					icmp_udp=packet.payload.payload.payload.payload
				#	pass #print "!!!!!!!!!!!!!!!!!!!\n"
				#	icmp_ip.show()
				#	pass #print packet.payload.src
				#	pass #print dummy_ip_where_packe_drop
					one_flow_set.add(icmp_udp.sport)
					one_flow_set.add(icmp_udp.dport)
				#	pass #print packet.payload.show()
			#		pass #print one_flow_set
					if source_ip in last_nodes_dict:
						last_nodes_dict[source_ip].append(one_flow_set)
					else:
						last_nodes_dict[source_ip]=[one_flow_set]
	#			pass #print "hello"
    	
	#	pass #print "ends here last node ",last_nodes_dict
	#	pass #print "server flow ",server_flow_array
	#	pass #print "ttl ",server_flow_ttl
		     #   	pass #print query_id_ttl
		# lets find true server of each las t ip of form ->->->
	#	pass #print "Last node dict "
		#pass #print server_flow_array
	#	pass #print last_nodes_dict
	#	pass #print server_flow_ttl
		for second_last_ip in last_nodes_dict.keys():
			all_flows=last_nodes_dict[second_last_ip]
			ttl_arr=[]
			if second_last_ip=="37.187.232.26":
				pass #print all_flows
				pass #print server_flow_array
				pass #print server_flow_ttl
				 
			for one_flow_of_second_last_ip in all_flows:
				if one_flow_of_second_last_ip in server_flow_array:
					relevant_index=server_flow_array.index(one_flow_of_second_last_ip)
					ttl_arr.append(server_flow_ttl[relevant_index])
					if second_last_ip=="37.187.232.26":
						pass #print relevant_index
						
						 

			dummy_arr=[]
			final_ttl_arr=sum(ttl_arr,dummy_arr) # concat
		#	pass #print "ttl of server ",final_ttl_arr
			if second_last_ip=="37.187.232.26" and dest=="178.32.114.231":
				#sys.exit()
				pass
			if len(final_ttl_arr)>0:
				server_ttl_value=min(final_ttl_arr)
				with open("./complete_stitched_paths/final_log",'a') as file:
					file.write(str(server_ttl_value)+" "+str(second_last_ip)+" ------> "+str(dest)+"\n\n\n")
				pass #print " final dekho phr : ",server_ttl_value," ",second_last_ip," ------> ",dest

                  

COUNT_DEST=0
COUND_DROP=0
COUNT_ANOMALY=0
PACK_DROP_RESPONSE=0
PACK_DROP_NO_RESPONSE=0
with open("MDA_DNS_scamper_output.txt",'r') as file:
	all_mda=file.read()

arr=all_mda.split("tracelb from")
arr=arr[1:]
count=1
count2=0
for trace in arr:
	pass #print "------------"
	pass #print trace
#	pass #print trace
	dest=trace.split(" ")[3]
	dest=dest[:-1]
	real_trace=trace.split("%")[1]
#	pass #print real_trace
	hops=real_trace.split("\n")
	terminal_nodes=[]
	dest_re_raw=dest
	dest_re=re.compile(re.escape(dest_re_raw))
	dest_found=False
	terminal_node_found=False


	for one_hop in hops:
		ip = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",one_hop)
		if dest in ip:
			#pass #print one_hop
			dest_found=True
			COUNT_DEST=COUNT_DEST+1
			with open("./complete_stitched_paths/final_log",'a') as file:
				file.write("MDA DNS - ICMP response of server - "+trace+"\n")
			break
		else: 
		#	pass #print "hey"
			if "-> * -> * -> * -> * -> *" in one_hop:
		#		pass #print "hey"
				terminal_nodes.append(one_hop)
				terminal_node_found=True

#	pass #print dest
#	pass #print terminal_nodes
	if terminal_node_found:
		dummy_ip_where_packe_drop=[]
		for one_node in terminal_nodes:
			ip=one_node.split("-> * -> * -> * -> *")[0].replace(" ","")
		#	pass #print "+++++++++\n",ip," +++++++++++++++++++"
			if "->" in ip:
				separate=ip.split("->")
				possible_ip=separate[len(separate)-1]
				
				possible_ip=re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",possible_ip)
				dummy_ip_where_packe_drop=dummy_ip_where_packe_drop+possible_ip
			else:
				possible_ip=re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",ip)
				dummy_ip_where_packe_drop=dummy_ip_where_packe_drop+possible_ip



		 
		COUND_DROP=COUND_DROP+1
	
		last_nodes=get_last_nodes(dest,dummy_ip_where_packe_drop,trace)
	# 	last_nodes.reverse()

	# 	if len(last_nodes)==0:
	# 		pass #print "server didnt respond ",dest
	# 		PACK_DROP_NO_RESPONSE=PACK_DROP_NO_RESPONSE+1
	# 		with open("./unreached/"+str(dest),'a') as file:
	# 			file.write(trace+"\n")			


	# 	if len(last_nodes)!=0:
			 
	# 		PACK_DROP_RESPONSE=PACK_DROP_RESPONSE+1
	# 		last_nodes=last_nodes[(0):15]
	# 		pass #print "last nodes "
	# 		pass #print last_nodes
			 
	# 		for one_node in terminal_nodes:
				 

	# 			pass #print "at this point dum ip",possible_ip
	# 			for one_ip in possible_ip:	
	# 				new_string=""
	# 				if one_ip in last_nodes:
	# 					pass #print "Bingo "
	# 					new_string=one_ip+" -> "+dest+"\n"
	# 					trace=trace+new_string
						
				
	# 		pass #print trace
	# 		with open("./complete_stitched_paths/"+str(dest),'a') as file:
	# 			file.write(trace+"\n")
	# 	pass #print "+++++++++++++++++",last_nodes,dest," !!! ",dummy_ip_where_packe_drop
	# 	sys.exit()		 	
	# 	#	sys.exit()
		
	# if not (terminal_node_found or dest_found):
	# 	pass #print "!!!!!! ",dest
	# 	COUNT_ANOMALY=COUNT_ANOMALY+1
	# 	with open("./anomaly/"+str(dest),'a') as file:
	# 			file.write(trace+"\n")

	
	# if  (terminal_node_found and not dest_found):
	# 	pass #print "!!!!!! ",dest
	# 	COUNT_ANOMALY=COUNT_ANOMALY+1
	 

	 


pass #print "dest found : ",COUNT_DEST
pass #print "pack drop : ",COUND_DROP
pass #print "among drop responded ",PACK_DROP_RESPONSE
pass #print "among drop no response ",PACK_DROP_NO_RESPONSE
pass #print "anomaly : ",COUNT_ANOMALY
