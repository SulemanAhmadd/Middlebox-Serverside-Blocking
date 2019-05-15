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
	with open(filename, "a+") as cmd_file:

		for dest_addr in input_list:
			domain = dest_addr[0]; ip = dest_addr[1];

			# shoaib, change below command for mda
			cmd_file.write('trace -P TCP -s %s -d 80 -F -H %s %s\n' % (str(sport), domain, ip))

def merge_output_files():
	os.system("cat output_mda_* >> mda-results.txt")
	os.system("rm output_mda_*")

def run_parser():
	#os.system('python parser_scripts/helper_main.py')
	pass

def print_completed_trace_count():
	os.system("(echo Total TCP-MDA completed: $(cat mda-results.txt | grep -c trace)) | tee -a log.txt")

def mv_to_folders():

	if os.path.exists('./TCP'):
		os.system('rm -r TCP/')

	os.system('mkdir TCP')
	os.system('mv mda-results.txt TCP/')

def remove_input_files():
	os.system("rm input_mda*")

def run_scamper(domain_list, thread_id):

	mdainput = 'input_mda' + str(thread_id) + '.txt'
	generate_input_files(domain_list, mdainput)

	mdaoutput = 'output_mda_' + str(thread_id) + '.txt'

	start = time.time()
	os.system("./run-scamper.sh %s %s" % (mdainput, mdaoutput)) #Todo handle dynamic name currently hardcoded
	end = time.time()

	print("Time: %d sec" % (end - start))

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
				domain_batch_list.append((domain, ip))
				count += 1;

	if len(domain_batch_list):
		exit()
		run_scamper(domain_batch_list, 1) # Dump scamper results

		remove_input_files() # Remove Intermediatory files
		merge_output_files()

		print_completed_trace_count() # Sanity Check

		mv_to_folders() # make folders and move
		#run_parser() # Run helper script

	print ("Total MDA destination addrs: %d" % count)

if __name__ == '__main__':

	if len(sys.argv) != 2:
		print("Usage: python run-exp.py [input-list]")
	else:
		os.system("sudo iptables -A OUTPUT -p tcp --tcp-flags ALL RST,RST -j DROP")
		os.system("sudo iptables -A OUTPUT -p tcp --tcp-flags ALL RST,ACK -j DROP")
		main(sys.argv[1])
		os.system("sudo iptables -D OUTPUT -p tcp --tcp-flags ALL RST,RST -j DROP")
		os.system("sudo iptables -D OUTPUT -p tcp --tcp-flags ALL RST,ACK -j DROP")