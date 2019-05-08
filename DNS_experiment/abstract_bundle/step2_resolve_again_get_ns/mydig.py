import sys
import dns.query
import dns.message
import re
import ipaddress
import time
import signal
import datetime
import random
import os
import sys
sys.path.insert(0, '/root')
from enum import Enum

cache = {}

root_servers = {}

root_servers['a'] = '198.41.0.4'
root_servers['b'] = '199.9.14.201'
root_servers['c'] = '192.33.4.12'
root_servers['d'] = '199.7.91.13'
root_servers['e'] = '192.203.230.10'
root_servers['f'] = '192.5.5.241'
root_servers['g'] = '192.112.36.4'
root_servers['h'] = '198.97.190.53'
root_servers['i'] = '192.36.148.17'
root_servers['j'] = '192.58.128.30'
root_servers['k'] = '193.0.14.129'
root_servers['l'] = '199.7.83.42'
root_servers['n'] = '202.12.27.33'


def output(hostname, rdtype, myresponse, elapsed, cnames):
	'''The output of the program
	
	Args:
		hostname (str): host to be queried
		rdtype (str): type A, NS, or MX
		myresponse (dns.message.Message): reponse from the DNS query
		elapsed (float): time elapsed
		cnames (list): cnames during a dns query
	'''
	
	#rdtype_dic = {1:'A', 2:'NS', 5:'CNAME'}
	
	
	answers = []
	for rrset in myresponse.answer:
		for item in rrset.items:
			answers.append(item.to_text())
			
	hostname_ = hostname + '.'
	
	number = str(30)
	for answer in answers:
		re_number = '(\d+)(.*)' + answers[0]
		match = re.search(re_number, myresponse.to_text())
		if match:
			number = match.group(1)
		number = str(number)
		break
	
	
	first_line = 'QUESTION SECTION:\n'
	second_line = hostname_.ljust(39) + 'IN'.ljust(5) + rdtype.ljust(5) + '\n\n'
	third_line = 'ANSWER SECTION:\n'
	forth_line = ''
	if len(cnames) > 0:
		left = hostname_
		for cname in cnames:
			forth_line = forth_line + left.ljust(33) + number.ljust(6) + 'IN'.ljust(5) + 'CNAME'.ljust(7) + cname + '\n'
			left = cname
		for answer in answers:
			forth_line = forth_line + left.ljust(33) + number.ljust(6) + 'IN'.ljust(5) + rdtype.ljust(7) + answer + '\n'
		if(len(answers)==0):
			forth_line=forth_line+"No Answer for domain "+hostname+"\n"
	else:    
		for answer in answers:
			forth_line = forth_line + hostname_.ljust(33) + number.ljust(6) + 'IN'.ljust(5) + rdtype.ljust(7) + answer + '\n'
		if(len(answers)==0):
			forth_line=forth_line+"No Answer for domain "+hostname+"\n"
	
	string = first_line + second_line + third_line + forth_line
	
	print('\n')
	print(string)
	
	cache[hostname + ' ' + rdtype] = string  # insert into global cache
	
	msg_size = str(len(string.replace(' ', '')))
	print('Query time: ' + str(int(elapsed * 1000)) + ' msec')
	print('WHEN:', datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"))
	print('MSG SIZE rcvd: ', msg_size, '\n')


def get_cname_from_rrset(rrset):
	'''Get CNAME from a RRset (from ANSWER section)
	
	Args:
		rrset (A DNS RRset): contains an CNAME to be extracted
		
	Returns:
		CNAME (str): the CNAME in the RRset
	'''
	try:
		item = rrset.items[0]
		return item.to_text()
	except Exception as e:
		print('Oops! Some issue with cname: ', e)


def get_ip_from_rrset(rrset):
	''' Get IP address from a RRset (from ADDITIONAL section)
	
	Args:
		rrset (A DNS RRset ): contains an IP address to be extracted
		
	Return:
		ip (str): the IP address in the RRset
	'''
	try:
		item = rrset.items[0]
		return item.to_text()
	except Exception as e:
		print('Oops! Some issue with ip: ', e)


def get_ns_from_authority(response):
	'''Get a name server from AUTHORITY.
	In some cases, there is no ADDITIONAL section, just AUTHORITY section!
	
	Args:
		response (dns.message.Message)
		
	Return:
		string: A name of ns server
	'''
	rrsets = response.authority[0].items
	index = random.randint(0, len(rrsets)-1)
	return rrsets[index].to_text() 


def check_hostname(hostname):
	'''Check whether a host is valid.
	
	Args:
		hostname (str): a hostname
		
	Return:
		True or False
	'''
	re_domain = '^(?=.{4,255}$)(([a-zA-Z0-9][a-zA-Z0-9-]{,61}[a-zA-Z0-9]\.)+|([a-zA-Z0-9-]{,61}[a-zA-Z0-9]\.)+)[a-zA-Z0-9]{2,5}.$'
	match = re.match(re_domain, hostname)

	if match:
		return True
	else:
		return False


def single_iterate(hostname, rdtype, where, timeout=1, dnssec=False):
	''' A single iterative DNS query
	
	Args:
		hostname (str): host to be queried
		rdtype (str): type A, NS, or MX
		where (str):  IP address of query destination
		dnssec (bool): whether use DNSSEC protocal or not
	Return: 
		response (dns.message.Message): the response of a single query
		
	Exception:
		May raise an exception
	'''
	a_query = dns.message.make_query(hostname, rdtype, want_dnssec=dnssec) 
	try:
		#print('single iterate: ', hostname, rdtype, where)
		response = dns.query.udp(a_query, where, timeout)
		return response
	except Exception as e:
		raise e  # Let the block who call this function catch the exception


def check_response(response, rdtype):
	'''Check whether the response has a valid IP address in its ANSWER section.
	
	Args:
		response (dns.message.Message): the response of a single query
		rdtype (str): type A=1, NS=2, CNAME=5, MX=15
	
	Return:
		True or False
	'''
	try:
		if rdtype == 'A':
			ip = get_ip_from_rrset(response.answer[0])
			ipaddress.ip_address(ip)
			return True
		elif rdtype == 'NS':                           # return NS when 'dig cnn.com NS'
			answer_type = response.answer[0].rdtype    # return all the CNAMEs when 'dig www.cnn.com NS'
			if answer_type == 2:
				return True                            # if NS, then return the answer
			elif answer_type == 5:
				return False                           # if CNAME, then keep looking for its NS
			else:
				return False                           # not sure if this condtion exist
		elif rdtype == 'MX':
			answer_type = response.answer[0].rdtype    # if MX, then return the answer
			if answer_type == 15:
				return True
			elif answer_type == 5:                     # if CNAME, then keep looking for its MX
				return False
			else:
				return False                           # not sure if this condtion exist
	except Exception as e:
		return False     

counter=0
stop_flag=False
timeout_flag=False
def handler(signum, frame):
	"""Exception handler to raise timeout errors for Selenium."""
	global stop_flag
	global timeout_flag
	stop_flag=True
	timeout_flag=True
	print("Query timeout!!!!!!!!!!!")
	print(timeout_flag)
	raise Exception("Timeout")
def dns_resolver_3(hostname, rdtype, cnames, name_servers,name_servers_answered,response_code,thread_number):
	''' My DNS resolver version 0.3
	
	Args:
		hostname (str): target hostname
		rdtype (str):   type A, NS, or MX
		cnames (list):  a list of CNAMES during a dns query
		
	Return:
		response (dns.message.Message): response of this dns query
	'''
	try:
		global counter
		global stop_flag
	  #  signal.signal(signal.SIGALRM, handler)
	   # signal.alarm(10)
		final_person=""
		counter=0
		for root in root_servers.values():
			try:

				counter=counter+1
				response = single_iterate(hostname, rdtype, root, timeout=0.5)
				if "SOA" in str(response.authority[0]):
					print("hey")
					stop_flag=True
					response_code.append((" ".join(str(response).split("\n"))))
					name_servers_answered.append((hostname,"root root root root "+str(root),"Could not get IP"))

					return ""
				print("!!!!----!!!")
				response_in_array=str(response).split("\n")
				print("oooooooooooo")
				print (response_in_array)
			
				if len(response.additional) == 0:
					continue                           # root doesn't have top level domain information
				while(len(response.answer)==0 ):       # if ANSWER section is empty, then keep iterating
					for one_authority_server in response.additional:
						if (not str(one_authority_server) in name_servers):
							name_servers.append(str(one_authority_server))
					
					if len(response.additional) > 0:   # use the IP in ADDITIONAL section
						for rrset in response.additional:
							next_ip = get_ip_from_rrset(rrset)
							try:
								response2 = single_iterate(hostname, rdtype, next_ip, timeout=0.5)
								 
								response_code.append((" ".join(str(response2).split("\n"))))
								response_array=str(response2).split("\n")
								response_code_string=response_array[2].split(" ")[1]
								print("This is what I received\n", response_array)
								print ("\n\n\n\n\n\nthread number is ",thread_number)
								print("\n\n\n\nstring  \n", response_code_string)
								print("cond  \n", response_code_string=="REFUSED")
								if "REFUSED"==response_code_string:
										stop_flag=True
										#print(dir(response2.rcode))
								#		print(response2.rcode)
										print("")
										name_servers_answered.append((hostname,str(rrset),"Could not get IP"))
										print("should go back")
										return ""

								if "SERVFAIL"==response_code_string:
										stop_flag=True
										#print(dir(response2.rcode))
								#		print(response2.rcode)
										print("")
										name_servers_answered.append((hostname,str(rrset),"Could not get IP"))
										print("should go back")
										return ""
								if len(response2.authority)>0:
									 
									if "SOA" in str(response2.authority[0]):
										print("''''''''''''''''''''''''''''''''''''''''''")
										stop_flag=True
										#print(dir(response2.rcode))
								#		print(response2.rcode)
										name_servers_answered.append((hostname,str(rrset),"Could not get IP"))
										return ""

									 

								response = response2
							 #   print("look")
							  #  print(rrset)
								final_person=rrset
								#print("(!!!!!)")
								break
							except Exception as e:
								if str(e)=="Timeout":
									print("Hostname which timed out "+hostname)
									for one_record in response.additional:
										name_servers_answered.append((hostname,str(one_record),"Could not get IP"))
									return ""
							   # print("whoop")
							  #  print(e)
								pass  # print('Oops! Authoratative server timeout, try next one. ', e)
					else:             # if both ANSWER and ADDITIONAL is empty, then find the IP of AUTHORITY  
						ns = get_ns_from_authority(response)
						 
						if check_hostname(ns):
							
							response2 = dns_resolver_3(ns, 'A', cnames,name_servers,name_servers_answered,response_code,thread_number)
							if stop_flag:
								return ""
							authority_answer = response2.answer[0]
							response.additional.append(authority_answer)  # add rrset that contains IP of a AUTHORITY to response
						else:
						
							return response   # hostname in AUTHORITY is not valid
				if check_response(response, rdtype):  # ip is in the response
					name_servers_answered.append((hostname,str(final_person),"IP"))
				#    print(response)
					return response

				else:                         # CNAME is in the response
					for rrset in response.answer:
						cname = get_cname_from_rrset(rrset)
						cnames.append(cname)
						name_servers_answered.append((hostname,str(final_person),"CNAME"))
						return dns_resolver_3(cname, rdtype, cnames,name_servers,name_servers_answered,response_code,thread_number)
				break
			except Exception as e:
				if str(e)=="Timeout":
					return ""
				pass   # print('Oops! Some error, start from a new root server.', e)
	except Exception as e:
		if str(e)=="Timeout":
			pass
			return ""
			
	print("hhehehe")    
 #   signal.alarm(0)

### DNSSEC #############################################################################################

trust_anchors = [
	# KSK-2017:
	dns.rrset.from_text('.', 1    , 'IN', 'DNSKEY', '257 3 8 AwEAAaz/tAm8yTn4Mfeh5eyI96WSVexTBAvkMgJzkKTOiW1vkIbzxeF3+/4RgWOq7HrxRixHlFlExOLAJr5emLvN7SWXgnLh4+B5xQlNVz8Og8kvArMtNROxVQuCaSnIDdD5LKyWbRd2n9WGe2R8PzgCmr3EgVLrjyBxWezF0jLHwVN8efS3rCj/EWgvIWgb9tarpVUDK/b58Da+sqqls3eNbuv7pr+eoZG+SrDK6nWeL3c6H5Apxz7LjVc1uTIdsIXxuOLYA4/ilBmSVIzuDWfdRUfhHdY6+cn8HFRm+2hM8AnXGXws9555KrUB5qihylGa8subX2Nn6UwNR1AkUTV74bU='),
	# KSK-2010:
	dns.rrset.from_text('.', 15202, 'IN', 'DNSKEY', '257 3 8 AwEAAagAIKlVZrpC6Ia7gEzahOR+9W29euxhJhVVLOyQbSEW0O8gcCjF FVQUTf6v58fLjwBd0YI0EzrAcQqBGCzh/RStIoO8g0NfnfL2MTJRkxoX bfDaUeVPQuYEhg37NZWAJQ9VnMVDxP/VHL496M/QZxkjf5/Efucp2gaD X6RS6CXpoY68LsvPVjR0ZSwzz1apAzvN9dlzEheX7ICJBBtuA6G3LQpz W5hOA2hzCTMjJPJ8LbqF6dsV6DoBQzgul0sGIcGOYl7OyQdXfZ57relS Qageu+ipAdTTJ25AsRTAoub8ONGcLmqrAmRLKBP1dfwhYB4N7knNnulq QxA+Uk1ihz0='),
]


rdtype_dic = {
	'A': 1      ,
	'NS':2      ,
	'DS':43     ,
	'RRSIG': 46 ,
	'DNSKEY':48 ,
}


def output_sec(hostname, rdtype, response, elapsed, cnames):
	'''The output of the program
	
	Args:
		hostname (str): host to be queried
		rdtype (str): type A, NS, or MX
		myresponse (dns.message.Message): reponse from the DNS query
		elapsed (float): time elapsed
		cnames (list): cnames during a dns query
	'''
  
	print('\n', 'QUESTION:')
	for i in response.question:
		print(i.to_text())
	
	print('\n', 'ANSWER:')
	for i in response.answer:
		print(i.to_text())
		
	print('\n')
	
	msg_size = str(len(myresponse.to_text()))
	print('Query time: ' + str(int(elapsed * 1000)) + ' msec')
	print('WHEN:', datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"))
	print('MSG SIZE rcvd: ', msg_size, '\n')


 


def get_rrset(response, rdtype):
	'''Get the desired rrset (DNSKEY, DS, A, NS), RRSIG and name from the response, their RRSIG
	
	Args:
		response (dns.message.Message): a response of a single iterative DNS query
		rdtype (str): rrset type
		
	Return:
		(rrset, rrsig, name) of desired rdtype
	'''
	try:
		if rdtype == 'DNSKEY' or rdtype == 'A':
			dnskey_or_a, rrsig, name = '', '', ''
			for rrset in response.answer:      # from observation, DNSKEY and A record is in ANSWER section
				if rrset.rdtype == rdtype_dic['RRSIG']:
					rrsig = rrset
				else:   # rrset.rdtype == rdtype_dic['DNSKEY'] or ['A']:
					dnskey_or_a = rrset
					name = rrset.name
			return dnskey_or_a, rrsig, name
		if rdtype == 'DS' or rdtype == 'NS':
			ds_or_ns, rrsig, name = '', '', ''
			for rrset in response.authority:   # from observation, DS and NS record is in AUTHORITY section
				if rrset.rdtype == rdtype_dic['RRSIG']:
					rrsig = rrset
				else:
					ds_or_ns = rrset
					name = rrset.name
			return ds_or_ns, rrsig, name
	except Exception as e:
		print('Oops! Bug in get_rrset')
		raise e  
 

def get_name_from_response(response):
	'''Get the next name(zone) in the dns query chain
	
	Args:
		response (dns.message.Message): a response that contains the next name or zone in the query chain
		
	Return:
		(str): next name
	'''
	name = ''
	try:
		rrset = response.authority[0]
		name = rrset.name.to_text()
	except Exception as e:
		raise e
	else:
		return name

 

class Flag(Enum):
	NO_ANSWER = 0
	HAVE_ANSWER = 1
	NO_DNSSEC = 2
	VERIFY_FAIL = 3


def dns_resolver_sec(hostname, rdtype, cnames):
	''' My DNS resolver version sec
	
	Args:
		hostname (str): target hostname
		rdtype (str):   type A, NS, or MX
		cnames (list):  a list of CNAMES during a dns query
		parent_response (dns.message.Message): a parent response that contains child's DS rrset
	Return:
		response (dns.message.Message): response of this dns query
	'''
	for root in root_servers.values():
		try:
			response = single_iterate(hostname, rdtype, root, timeout=0.5, dnssec=True)
			response_dnskey = single_iterate('.', 'DNSKEY', root, timeout=0.5, dnssec=True)
			name_key, dnskey = verify_dnskey(response_dnskey)
			verify_ds(response, name_key, dnskey)
			verify_root(dnskey)
			response2 = None
			response_dnskey2 = None
			if len(response.additional) == 0:
				continue                           # root doesn't have top level domain information
			flag = Flag.NO_ANSWER            # flag traces whether ANSWER section is empty or not
			while flag == Flag.NO_ANSWER:                            
				if len(response.additional) > 0:   # use the IP in ADDITIONAL section
					nextname = get_name_from_response(response)
					for rrset in response.additional:
						next_ip = get_ip_from_rrset(rrset)
						try:
							response2 = single_iterate(hostname, rdtype, next_ip, timeout=0.5, dnssec=True)
							response_dnskey2 = single_iterate(nextname, 'DNSKEY', next_ip, timeout=0.5, dnssec=True)

							if len(response2.answer) != 0:
								flag = Flag.HAVE_ANSWER
								break
							if check_ds_exist(response2) == False:
								flag = Flag.NO_DNSSEC
								break
							if nextname == 'org.': # for org. zone, when dnssec=True, DNSKEY response is empty
								name_key, dnskey = verify_org_dnskey(next_ip) # so I wrote special functions for org.
								verify_ds(response2, name_key, dnskey)
								verify_org_zone(dnskey, response)
							else:
								name_key, dnskey = verify_dnskey(response_dnskey2)
								verify_ds(response2, name_key, dnskey)
								verify_zone(response_dnskey2, response)
							
							response = response2
							response_dnskey = response_dnskey2
							break
						except Exception as e:
							pass  #print('Oops!', e)
				else:             # if both ANSWER and ADDITIONAL is empty, then find the IP of AUTHORITY  
					ns = get_ns_from_authority(response)
					if check_hostname(ns):
						response2 = dns_resolver_3(ns, 'A', cnames)
						authority_answer = response2.answer[0]
						response.additional.append(authority_answer)  # add rrset that contains IP of a AUTHORITY to response
					else:
						 return response   # hostname in AUTHORITY is not valid
			if flag == Flag.NO_DNSSEC:
				return flag, response2
			
			if check_response(response2, rdtype):  # ip is in the response
				try:
					name_key, dnskey = verify_dnskey(response_dnskey2)
					verify_a(response2, name_key, dnskey)
					verify_zone(response_dnskey2, response)
				except Exception as e:
					print(e)
					flag = Flag.VERIFY_FAIL
					return flag, response2
				else:
					return flag, response2
			else:                         # CNAME is in the response
				for rrset in response.answer:
					cname = get_cname_from_rrset(rrset)
					cnames.append(cname)
					return dns_resolver_sec(cname, rdtype, cnames)
			break
		except Exception as e:
			print(e)

########################################################################################################

def alias(array):
	if len(array) == 3:
		print("------------------------------")
		thread_number=str(array[0])
		hostname = array[1]
		rdtype   = array[2]
		hostname=hostname.split(" ")[0]
		global counter
		global stop_flag
		cnames = []
		name_servers=[]
		name_servers_answered=[]
		response_code=[]
		start = time.time()
		pass
		signal.signal(signal.SIGALRM, handler)
		signal.alarm(50)
		myresponse = dns_resolver_3(hostname, rdtype, cnames,name_servers,name_servers_answered,response_code,thread_number)
		signal.alarm(0)
		elapsed = time.time() - start
		
		 
		if myresponse!="" and myresponse is not None:
			output(hostname, rdtype, myresponse, elapsed, cnames)
		print("Name servers who responded with IP \n",name_servers_answered)
		length=len(name_servers_answered)
		print("!!!!!!!!!!!!!!!!!!")
		print(myresponse)
		print("!!!!!!!!!!!!!!!!!!")
		if length!=0 and (name_servers_answered[length-1][2]=="IP") and myresponse:
			one_name_server=name_servers_answered[length-1]
			
			print("This gave answer ",one_name_server[1].split()[4])
			answers = []
			for rrset in myresponse.answer:
				for item in rrset.items:
					answers.append(item.to_text())
					
			hostname_ = hostname + '.'
			
			number = str(30)
			for answer in answers:
				re_number = '(\d+)(.*)' + answers[0]
				match = re.search(re_number, myresponse.to_text())
				if match:
					number = match.group(1)
				number = str(number)
				break
			print("answer ",answers)
			with open(thread_number+"trac_domains_resolved",'a') as file1:
				file1.write(str(name_servers_answered[length-1][0])+" "+str(one_name_server[1].split()[4])+" "+str(answers[0])+"\n")
		else:
			pass
			print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",hostname)
			global timeout_flag
			real_host=""
			real_host_domain=""
			if len(cnames)==0:
				real_host=hostname
				real_host_domain=hostname
			else:
				real_host=cnames[len(cnames)-1]
				real_host_domain=cnames[len(cnames)-1]

			for one_name_server in name_servers_answered:
				print("one name server is ",one_name_server)
				if one_name_server[2]=="Could not get IP" and one_name_server[0]==real_host_domain:
					print("HELLO")
					# sometimes multiple nameserver comes delimited by \n but on file appar together
					name_server_string=""
					if '\n' in one_name_server[1]:
						print("n present")
						separate=one_name_server[1].split("\n")
						print(separate)
						for one_server in separate:

							name_server_string=name_server_string+one_server+" "
							print (one_server)
							print("see below full string")
							print(name_server_string)
					else:
						print("n NOT present")
						name_server_string=one_name_server[1]
					print("appending this to final list",name_server_string)
					real_host=real_host+" "+name_server_string+" "
			if len(response_code)>0:
				message=""
				message=real_host_domain+" "+str(response_code[len(response_code)-1])
				print("++++++++++++++++++++++++++++++++++++++++++++++")
				print(timeout_flag)
				if(timeout_flag):
					message=message+" "+"Domain_timed_out"
				message=message+"\n"	
				with open(thread_number+"trac_last_response_received.txt",'a') as file10:
					file10.write(message)

			final_string=""
			for i in real_host:
				if i!='\n':
					final_string=final_string+i
			with open(thread_number+"trac_blocked_domain_ns_info.txt",'a') as file1:
				file1.write(str(final_string)+"\n")

		print("\n\nAll servers contacted\n",name_servers)
		print("\n cnames contacted \n",cnames)
		if stop_flag==True:
			print("\n\nCname for domain which timed out or SOA record\n",cnames)

		print("------------------------------") 
		stop_flag=False
		timeout_flag=False
		counter=0

if __name__ == '__main__':
	print()
	alias(sys.argv)
	
