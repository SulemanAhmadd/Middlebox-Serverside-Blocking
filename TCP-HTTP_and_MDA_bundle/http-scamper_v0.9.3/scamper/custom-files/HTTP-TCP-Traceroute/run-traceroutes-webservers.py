import subprocess
import threading
import thread
import time
import sys 
import os

if os.path.exists('./../http_payload'):
	os.system('rm -rf ./../http_payload')
os.system('mkdir ./../http_payload/')

def parse_input_line(line):
	line = line.strip().split()
	domain = line[0].strip(',')
	ip = line[1].strip(',')

	return domain, ip

def generate_input_files(input_list, filename1, filename2):
	with open(filename1, "a+") as non_http_cmd, open(filename2, "a+") as http_cmd:

		for dest_addr in input_list:
			domain = dest_addr[0]; ip = dest_addr[1]; sport = dest_addr[3]; 

			if dest_addr[2]:
				non_http_cmd.write('trace -g 5 -P TCP -s %s -d 80 %s\n' % (str(sport), ip))
				http_cmd.write('trace -g 5 -P TCP -s %s -d 80 -F -H %s %s\n' % (str(sport), domain, ip))
			else:
				http_cmd.write('trace -P TCP -s %s -d 80 -F -H %s %s\n' % (str(sport), domain, ip))

def merge_output_files():
	os.system("cat output_http_* >> http-results.txt")
	os.system("cat output_nonhttp_* >> nonhttp-results.txt")

	os.system("rm -rf output_http_*")
	os.system("rm -rf output_nonhttp_*")

def run_parser():
	os.system('python parser_scripts/helper_main.py')

def print_completed_trace_count():
	os.system("(echo Total HTTP-Traceroutes completed: $(cat http-results.txt | grep -c trace)) | tee -a log.txt")
	os.system("(echo Total nonHTTP-Traceroutes completed: $(cat nonhttp-results.txt | grep -c trace)) | tee -a log.txt")

def mv_to_folders():

	if os.path.exists('./TCP'):
		os.system('rm -r TCP/')

	if os.path.exists('./HTTP'):
		os.system('rm -r HTTP/')

	os.system('mkdir TCP'); os.system('mv nonhttp-results.txt TCP/');
	os.system('mkdir HTTP'); os.system('mv http-results.txt HTTP/');
	os.system('mv ./../http_payload/ HTTP/')

def remove_input_files():
	os.system("rm -rf input_nonhttp_*")
	os.system("rm -rf input_http_*")

def run_scamper(domain_list, thread_id):

	httpinput = 'input_http_' + str(thread_id) + '.txt'
	nonhttpinput = 'input_nonhttp_' + str(thread_id) + '.txt'

	generate_input_files(domain_list, nonhttpinput, httpinput)

	httpoutput = 'output_http_' + str(thread_id) + '.txt'
	nonhttpoutput = 'output_nonhttp_' + str(thread_id) + '.txt'

	start = time.time()
	os.system("./run-scamper.sh %s %s %s %s" % (httpinput, nonhttpinput, httpoutput, nonhttpoutput)) #Todo handle dynamic name currently hardcoded
	end = time.time()

	print("Time: %d sec" % (end - start))

def main(input_filename):

	'''
	Ignore these IPS
	'''
	restricted_address = ['127.0.0.1', '255.255.255.255', '0.0.0.0', '0.0.0.1']
	unique_ips_set = set()
	sport = 20000

	http_count = 0
	nonhttp_count = 0

	domain_batch_list = []

	'''
	Parse Input
	'''
	with open(input_filename, "r") as resolved_list, open("invalid-ips.txt", "a+") as invalid:

		for dest_addr in resolved_list:

			if sport > 40000:
				sport = 20000

			domain, ip = parse_input_line(dest_addr)

			if ip in restricted_address:
				invalid.write('%s %s\n' % (domain, ip))

			elif ip in unique_ips_set:
				domain_batch_list.append((domain, ip, False, sport))
				sport += 1; http_count += 1;

			else:
				domain_batch_list.append((domain, ip, True, sport))

				unique_ips_set.add(ip)
				sport += 1; http_count += 1; nonhttp_count += 1;

	if len(domain_batch_list):

		run_scamper(domain_batch_list, 1) # Dump scamper results

		remove_input_files() # Remove Intermediatory files
		merge_output_files()

		print_completed_trace_count() # Sanity Check

		mv_to_folders() # make folders and move
		run_parser() # Run helper script

	print ("Total HTTP destination addrs: %d" % http_count)
	print ("Total Non-HTTP destination addrs: %d" % nonhttp_count)

if __name__ == '__main__':

	if len(sys.argv) != 2:
		print("Usage: python run-exp.py [input-list]")
	else:
		os.system("sudo iptables -A OUTPUT -p tcp --tcp-flags ALL RST,RST -j DROP")
		os.system("sudo iptables -A OUTPUT -p tcp --tcp-flags ALL RST,ACK -j DROP")
		main(sys.argv[1])
		os.system("sudo iptables -D OUTPUT -p tcp --tcp-flags ALL RST,RST -j DROP")
		os.system("sudo iptables -D OUTPUT -p tcp --tcp-flags ALL RST,ACK -j DROP")
