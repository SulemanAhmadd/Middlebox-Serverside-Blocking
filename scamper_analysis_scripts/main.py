from trace import Trace
from analysis import Analysis
import sys
import os

HTTP_RESULT_FILE = 'http-results.txt'
NONHTTP_RESULT_FILE = 'nonhttp-results.txt'
PAYLOAD_FILE = 'http_payload'

vantage_point_dic = {}

'''
{VP: {190.190.190.190: [http-trace, udp-trace, icmp-trace, tcp-trace]}, ...}

Later:
{VP: {domain: [http-trace, udp-trace, icmp-trace, tcp-trace]}, ...}
'''

def make_dest_dict(http_traces, nonhttp_traces):
	traces_dict = {}
	for http_trace in http_traces:

		traces = []
		destination = http_trace.get_destination()
		traces.append(http_trace)

		if destination in traces_dict: # Remove after domain addition
			continue;

		for nonhttp_trace in nonhttp_traces: # can be improved n^2 for now
			if nonhttp_trace.get_destination() == destination:
				traces.append(nonhttp_trace)

		traces_dict[destination] = traces

	return traces_dict

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

def parse_traces(filename):

	trace_objects = []
	trace = []; trace_type = '';
	with open(filename, 'r') as traces_file:

		for line in traces_file:
			line = process_line(line)

			if 'traceroute' in line[0] and trace:
				trace_objects.append(Trace(trace_type, trace))
				trace = []; trace_type = '';

			trace_type += get_trace_type(line)
			trace.append(line)

	return trace_objects

def main():

	root_directory = os.getcwd()

	'''
	Data Parsing
	'''

	for vantage_point in next(os.walk(root_directory))[1]:

		vantage_point_dir = os.path.join(root_directory, vantage_point)

		http_trace_file = os.path.join(vantage_point_dir, HTTP_RESULT_FILE)
		nonhttp_trace_file = os.path.join(vantage_point_dir, NONHTTP_RESULT_FILE)
		raw_html_file = os.path.join(vantage_point_dir, PAYLOAD_FILE)

		http_traces = parse_traces(http_trace_file) # returns a list of trae objects
		nonhttp_traces = parse_traces(nonhttp_trace_file)
		'''
		# TODO: HTML Parsing
		'''

		traces_dict = make_dest_dict(http_traces, nonhttp_traces) # merge both trace lists based on common dest ip
		vantage_point_dic[vantage_point] = traces_dict # Update dict of vantage point 

	'''
	Data Analysis

	1. Three hop difference analysis
	2. How many traceroutes completed
	3. How many http responses
	'''

	analysis = Analysis()
	analysis.get_total_traceroutes_completed()

if __name__ == '__main__':
	main()