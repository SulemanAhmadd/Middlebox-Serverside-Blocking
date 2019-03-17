from trace import Trace
from analysis import Analysis
import sys
import os

HTTP_RESULT_FILE = 'http-results.txt'
NONHTTP_RESULT_FILE = 'nonhttp-results.txt'
PAYLOAD_FILE = 'http_payload'

vantage_point_dic = {}

'''
Prev:
{VP: {dest: [http-trace, udp-trace, icmp-trace, tcp-trace]}, ...}

Now:
{VP: {http: {dest:[trace]}, icmp:{dest:[trace,...]}, ... }}
'''

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

	if trace_object.get_destination() in inner_dict:
		inner_dict[trace_object.get_destination()].append(trace_object)
	else:
		inner_dict[trace_object.get_destination()] = [trace_object]

def parse_traces(filename, traces_dict):

	trace = []; trace_type = '';
	with open(filename, 'r') as traces_file:

		for line in traces_file:
			line = process_line(line)

			if 'traceroute' in line[0] and trace:
				add_dest_to_dict(traces_dict, Trace(trace_type, trace))
				trace = []; trace_type = '';

			trace_type += get_trace_type(line)
			trace.append(line)

		# Add the last traceroute of file
		add_dest_to_dict(traces_dict, Trace(trace_type, trace))

def main():

	root_directory = os.getcwd()

	'''
	Data Parsing
	'''
	for vantage_point in next(os.walk(root_directory))[1]:

		traces_dict = {
			'http' : {},
			'tcp'  : {},
			'icmp' : {},
			'udp'  : {}
		}

		vantage_point_dir = os.path.join(root_directory, vantage_point)

		http_trace_file = os.path.join(vantage_point_dir, HTTP_RESULT_FILE)
		nonhttp_trace_file = os.path.join(vantage_point_dir, NONHTTP_RESULT_FILE)
		raw_html_file = os.path.join(vantage_point_dir, PAYLOAD_FILE)

		parse_traces(http_trace_file, traces_dict) # returns a list of trace objects
		parse_traces(nonhttp_trace_file, traces_dict)
		'''
		# TODO: HTML Parsing
		'''
		vantage_point_dic[vantage_point] = traces_dict # Update dict of vantage point 
		break

	'''
	Data Analysis

	1. Three hop difference analysis
	2. How many traceroutes completed
	3. How many http responses
	'''

	analysis = Analysis()
	analysis.get_total_traceroutes_not_initialized(vantage_point_dic)

if __name__ == '__main__':
	main()