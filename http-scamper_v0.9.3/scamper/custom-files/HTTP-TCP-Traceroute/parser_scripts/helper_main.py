from trace import Trace
import sys
import os

HTTP_RESULT_FILE = './HTTP/http-results.txt'
HTTP_OUT_FILE = './HTTP/second_last_ip.txt'
NONHTTP_RESULT_FILE = './TCP/nonhttp-results.txt'
TCP_OUT_FILE = './TCP/second_last_ip.txt'

domain_ip_map = {}

def process_line(input_line):
	return [x for x in input_line.strip().split(' ') if x]

def get_trace_type(line):
	if 'traceroute' in line[0]:
		if 'http' in line[0]:
			return 'http'
		elif 'udp' in line[0]:
			return 'udp'
		elif 'tcp' in line[0]:
			return 'tcp'
		elif 'icmp' in line[0]:
			return 'icmp'
		else:
			sys.exit('Cannot understand trace')
	return ''

def add_dest_to_dict(traces_dict, trace_object):

	inner_dict = traces_dict[trace_object.trace_type]

	if trace_object.trace_type == 'http':

		if trace_object.dest_addr in domain_ip_map:
			domain_ip_map[trace_object.dest_addr].append(trace_object.domain_name)
		else:
			domain_ip_map[trace_object.dest_addr] = [trace_object.domain_name]

		inner_dict[trace_object.domain_name] = trace_object
	else:

		for domain in domain_ip_map[trace_object.dest_addr]:
			inner_dict[domain] = trace_object


def parse_traces(filename, traces_dict):

	trace = []; trace_type = '';
	with open(filename, 'r') as traces_file:

		for line in traces_file:
			line = process_line(line)
			if not line: continue;

			if 'traceroute' in line[0] and trace:
				add_dest_to_dict(traces_dict, Trace(trace_type, trace))
				trace = []; trace_type = '';

			trace_type += get_trace_type(line)
			trace.append(line)

		# Adds the last traceroute of file
		add_dest_to_dict(traces_dict, Trace(trace_type, trace))

def parse_webpages(webpage_dir, webpage_dict):
	for webpage in os.listdir(webpage_dir):
		webpage_path = os.path.join(webpage_dir, webpage)

		obj = Webpage(webpage_path)
		obj.parse_webpage(webpage_path)

		webpage_dict[webpage] = obj


def main():

	root_directory = os.getcwd()

	traces_dict = {
		'http' : {},
		'tcp'  : {},
		'icmp' : {},
		'udp'  : {}
	}

	'''
	Data Parsing
	'''
	parse_traces(HTTP_RESULT_FILE, traces_dict)
	parse_traces(NONHTTP_RESULT_FILE, traces_dict)

	'''
	Data Analysis
	'''

	for dest_addr in traces_dict['http'].keys():
		http_trace = traces_dict['http'][dest_addr]
		tcp_trace = traces_dict['tcp'][dest_addr]

		# HTTP
		if http_trace.trace_started and http_trace.reply_hop.reply_recv:

			with open(HTTP_OUT_FILE, 'a+') as http_file:

				if not http_trace.path_hops[http_trace.path_length - 2].reply_addrs:
					http_file.write(dest_addr + ',' + '*' + '\n')
				else:
					for addr in http_trace.path_hops[http_trace.path_length - 2].reply_addrs:
						http_file.write(dest_addr + ',' + addr + '\n')

		# TCP
		if tcp_trace.trace_started and tcp_trace.reply_hop.reply_recv:

			with open(TCP_OUT_FILE, 'a+') as tcp_file:


				if not tcp_trace.path_hops[tcp_trace.path_length - 2].reply_addrs:
					tcp_file.write(dest_addr + ',' + '*' + '\n')
				else:
					for addr in tcp_trace.path_hops[tcp_trace.path_length - 2].reply_addrs:
						tcp_file.write(dest_addr + ',' + addr + '\n')
	
if __name__ == '__main__':
	main()