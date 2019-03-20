from trace import Trace
from webpage import Webpage
from analysis import Analysis
import cPickle as pickle
import sys
import os

HTTP_RESULT_FILE = 'http-results.txt'
NONHTTP_RESULT_FILE = 'nonhttp-results.txt'
PAYLOAD_FILE = 'http_payload'
CACHE_DIR = './cache'

vantage_point_trace_dict = {}
vantage_point_webpage_dict = {}
domain_ip_map = {}

'''
Data structures

Traces Dict:
{VP: {http: {domain: trace}, icmp:{domain: trace}, ... }}

{VP: {domain: webpage, domain2: webpage}}
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

		webpage_dict[webpage.strip('.txt')] = obj

def exists_cache_json(vantage_point):
	return os.path.exists(os.path.join(CACHE_DIR, vantage_point))

def save_cache_json(vantage_point, traces_dict):

	if not os.path.exists(CACHE_DIR):
	    os.mkdir(CACHE_DIR)

	with open(os.path.join(CACHE_DIR, vantage_point), 'wb') as handle:
		pickle.dump(traces_dict, handle)

def load_cache_json(vantage_point, traces_dict):
	with open('file.txt', 'rb') as handle:
		traces_dict = pickle.loads(handle.read())

def main():

	root_directory = os.getcwd()

	'''
	Data Parsing
	'''
	for vantage_point in next(os.walk(root_directory))[1]:

		if vantage_point == CACHE_DIR:
			continue

		traces_dict = {
			'http' : {},
			'tcp'  : {},
			'icmp' : {},
			'udp'  : {}
		}

		webpages_dict = {}

		if not exists_cache_json(vantage_point):

			vantage_point_dir = os.path.join(root_directory, vantage_point)

			http_trace_file = os.path.join(vantage_point_dir, HTTP_RESULT_FILE)
			nonhttp_trace_file = os.path.join(vantage_point_dir, NONHTTP_RESULT_FILE)
			raw_html_file = os.path.join(vantage_point_dir, PAYLOAD_FILE)

			parse_traces(http_trace_file, traces_dict) # returns a list of trace objects
			parse_traces(nonhttp_trace_file, traces_dict)

			parse_webpages(os.path.join(root_directory, vantage_point, PAYLOAD_FILE), webpages_dict)

			# save_cache_json(vantage_point, traces_dict) <-- disabled for now
			# save_cache_json(vantage_point + '.page', webpages_dict) <-- disabled for now
		else:

			load_cache_json(vantage_point, traces_dict)
			load_cache_json(vantage_point + '.page', webpages_dict)

		domain_ip_map.clear()

		vantage_point_trace_dict[vantage_point] = traces_dict # Update dict of vantage point traces
		vantage_point_webpage_dict[vantage_point] = webpages_dict # Update dict of vantage point webpages

	'''
	Data Analysis

	'''
	analysis = Analysis()

	print('> Failed Initilizations per VP')
	analysis.get_total_traceroutes_not_initialized(vantage_point_trace_dict)
	print('\n')
	print('> Hop Count Difference for HTTP lesser')
	analysis.compare_for_n_hop_diff_and_avg_pathlen(vantage_point_trace_dict, 3, inverse=False)
	print('\n')
	print('> Hop Count Difference for HTTP greater')
	analysis.compare_for_n_hop_diff_and_avg_pathlen(vantage_point_trace_dict, 0, inverse=True)
	print('\n')
	print('> Last Hop Analysis')
	analysis.get_total_traceroutes_lasthop_analysis(vantage_point_trace_dict)
	print('\n')
	print('> Status codes per VP without externel crawler')
	analysis.get_status_codes(vantage_point_webpage_dict)
	print('\n')
	print('> Complete Webpages')
	analysis.get_total_complete_webpages(vantage_point_webpage_dict)
	print('\n')
	print('> Replacing Invalid wepages')
	analysis.replace_webpages_using_external_crawler(vantage_point_webpage_dict)
	print('\n')
	print('> Status codes per VP after externel crawler')
	analysis.get_status_codes(vantage_point_webpage_dict)
	print('\n')
	print('> Complete Webpages after externel crawler')
	analysis.get_total_complete_webpages(vantage_point_webpage_dict)
	print('\n')

if __name__ == '__main__':
	main()