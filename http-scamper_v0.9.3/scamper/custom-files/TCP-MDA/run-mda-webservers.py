import subprocess
import threading
import thread
import time
import sys 
import os

def parse_input_line(line):
	line = line.strip().split()
	domain = line[0].strip(',')
	ip = line[1].strip(',')

	return domain, ip

def generate_input_files(input_list, filename):
	os.system("pwd")
	with open("scamper_commands.txt", "a") as cmd_file:

		for dest_addr in input_list:
			domain = dest_addr[0]; ip = dest_addr[1];

			# shoaib, change below command for mda
			cmd_file.write('trace -P TCP -s %s -d 80 -F -H %s %s\n')
  
def run_scamper(domain_list, thread_id):

	mdainput = 'input_mda' + str(thread_id) + '.txt'
	generate_input_files(domain_list, mdainput)

	mdaoutput = 'output_mda_' + str(thread_id) + '.txt'


def main(input_filename):

	'''
	Ignore these IPS
	'''
	restricted_address = ['127.0.0.1', '255.255.255.255', '0.0.0.0', '0.0.0.1']
	unique_ips_set = set()

	count = 0

	domain_batch_list = []

	'''
	Parse Input
	'''
	with open(input_filename, "r") as resolved_list, open("invalid-ips.txt", "a+") as invalid:

		for dest_addr in resolved_list:

			domain, ip = parse_input_line(dest_addr)

			if ip in restricted_address:
				invalid.write('%s %s\n' % (domain, ip))

			elif ip not in unique_ips_set:
				unique_ips_set.add(ip)
				domain_batch_list.append((domain, ip))
				with open("scamper_command.txt",'a') as file:
					file.write("tracelb -P tcp-sport -d 80 "+ip+"\n")
				count += 1;


if __name__ == '__main__':

	if len(sys.argv) != 2:
		print("Usage: python run-exp.py [input-list]")
	else:
		os.system("sudo iptables -A OUTPUT -p tcp --tcp-flags ALL RST,RST -j DROP")
		os.system("sudo iptables -A OUTPUT -p tcp --tcp-flags ALL RST,ACK -j DROP")
		main(sys.argv[1])
		os.system("sudo iptables -D OUTPUT -p tcp --tcp-flags ALL RST,RST -j DROP")
		os.system("sudo iptables -D OUTPUT -p tcp --tcp-flags ALL RST,ACK -j DROP")
