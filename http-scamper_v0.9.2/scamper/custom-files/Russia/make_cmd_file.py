import sys
import socket

input_file = open(sys.argv[1], 'r')
input_list = input_file.readlines()
input_file.close()


restricted_address = ['127.0.0.1', '255.255.255.255', '0.0.0.0', '0.0.0.1']
unique_ips = set()

sport = 20000;
with open("nonhttp_cmd_file.txt", "a+") as non_http_cmd, open("http_cmd_file.txt", "a+") as http_cmd, open("invalid.txt", "a+") as invalid:
	for element in input_list:
		if sport > 40000:
			sport = 20000;

		element = element.strip().split()
		domain = element[0].strip(',')
		ip = element[1].strip(',')

		if ip in restricted_address:
			invalid.write('%s %s\n' %(domain, ip))
		
		elif ip in unique_ips:
			http_cmd.write('trace -P TCP -s %s -d 80 -F -H %s %s\n' % (str(sport), domain, ip))
			sport += 1

		else:
			non_http_cmd.write('trace -P TCP -s %s -d 80 %s\n' % (str(sport), ip))
			non_http_cmd.write('trace -P UDP-paris -d 53 %s\n' % (ip))
			non_http_cmd.write('trace -P ICMP-paris %s\n' % (ip))

			http_cmd.write('trace -P TCP -s %s -d 80 -F -H %s %s\n' % (str(sport), domain, ip))

			sport += 1
			unique_ips.add(ip)