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

def generate_input_files(input_list, filename1, filename2):
	with open(filename1, "a+") as non_http_cmd, open(filename2, "a+") as http_cmd:

		for dest_addr in input_list:
			domain = dest_addr[0]; ip = dest_addr[1]; sport = dest_addr[3]; 

			if dest_addr[2]:
				non_http_cmd.write('trace -P TCP -s %s -d 80 %s\n' % (str(sport), ip))
				non_http_cmd.write('trace -P ICMP-paris %s\n' % (ip))
				http_cmd.write('trace -P TCP -s %s -d 80 -F -H %s %s\n' % (str(sport), domain, ip))
			else:
				http_cmd.write('trace -P TCP -s %s -d 80 -F -H %s %s\n' % (str(sport), domain, ip))

def merge_output_files():
	os.system("cat output_http_* >> http-results.txt")
	os.system("cat output_nonhttp_* >> nonhttp-results.txt")

	os.system("rm output_http_*")
	os.system("rm output_nonhttp_*")

def print_completed_trace_count():
	os.system("(echo Total HTTP-Traceroutes completed: $(cat http-results.txt | grep -c trace)) | tee -a log.txt")
	os.system("(echo Total nonHTTP-Traceroutes completed: $(cat nonhttp-results.txt | grep -c trace)) | tee -a log.txt")

def remove_input_files():
	os.system("rm input_nonhttp_*")
	os.system("rm input_http_*")

def run_scamper(domain_list, thread_id):

	httpinput = 'input_http_' + str(thread_id) + '.txt'
	nonhttpinput = 'input_nonhttp_' + str(thread_id) + '.txt'

	generate_input_files(domain_list, nonhttpinput, httpinput)

	httpoutput = 'output_http_' + str(thread_id) + '.txt'
	nonhttpoutput = 'output_nonhttp_' + str(thread_id) + '.txt'

	start = time.time()
	os.system("./run-scamper.sh %s %s %s %s" % (httpinput, nonhttpinput, httpoutput, nonhttpoutput)) #Todo handle dynamic name currently hardcoded
	end = time.time()

	print("Time: %d" % (end - start))

def main():
	input_filename = sys.argv[1]
	vantage_point = sys.argv[2]
	batch_size = int(sys.argv[3])
	num_threads = int(sys.argv[4])

	restricted_address = ['127.0.0.1', '255.255.255.255', '0.0.0.0', '0.0.0.1']
	thread_workload = int(batch_size / num_threads)
	domain_batch_list = []
	unique_ips_set = set()
	sport = 20000

	http_count = 0
	nonhttp_count = 0

	with open(input_filename, "r") as resolved_list, open("invalid.txt", "a+") as invalid:

		domain_batch_list = []
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

			if len(domain_batch_list) == batch_size:

				threads_list = [];
				for thread_start_index in range(0, len(domain_batch_list), thread_workload):
					batch_chunk = domain_batch_list[thread_start_index: thread_start_index + thread_workload]

					thread = threading.Thread(target=run_scamper, args=(batch_chunk, len(threads_list) + 1,))
					thread.start()

					threads_list.append(thread)

				for thread in threads_list:
					thread.join()

				domain_batch_list = []
				remove_input_files()
				merge_output_files()
				print_completed_trace_count()

				exit()

	print ("Total HTTP destination addrs: %d" % http_count)
	print ("Total Non-HTTP destination addrs: %d" % nonhttp_count)

if __name__ == '__main__':

	if len(sys.argv) != 5:
		print("Usage: python run-exp.py [input-list] [vantage-point] [batch-size] [num-threads]")
	elif (int(sys.argv[3]) < int(sys.argv[4])):
		print("Cannot assign more threads to a small batch size")
	else:
		os.system("sudo iptables -A OUTPUT -p tcp --tcp-flags ALL RST,RST -j DROP")
		os.system("sudo iptables -A OUTPUT -p tcp --tcp-flags ALL RST,ACK -j DROP")
		main()
		os.system("sudo iptables -D OUTPUT -p tcp --tcp-flags ALL RST,RST -j DROP")
		os.system("sudo iptables -D OUTPUT -p tcp --tcp-flags ALL RST,ACK -j DROP")