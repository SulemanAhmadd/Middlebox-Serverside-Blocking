#import matplotlib as plt

def verify_reponse_type(reply_hop, trace_type):
	for resp_ip in reply_hop.dest_resps.keys():

		for resp_type in reply_hop.dest_resps[resp_ip]:

			if trace_type == 'http' and 'TCP' in resp_type:
				return True

			elif trace_type == 'udp' and '' in resp_type:
				return True

			elif trace_type == 'tcp' and ('TCP' in resp_type or 'SYN' in resp_type):
				return True

			elif trace_type == 'icmp':
				return True
	return False


class Analysis(object):

	def get_total_traceroutes_not_initialized(self, _vantage_point_dic):
		
		for vantage_point in _vantage_point_dic:

			trace_dict_initalize_count = {
			'http' : 0,
			'tcp'  : 0,
			'icmp' : 0,
			'udp'  : 0
			}

			for dest_addr in _vantage_point_dic[vantage_point]['http'].keys():

				for protocol in trace_dict_initalize_count.keys():

					trace = _vantage_point_dic[vantage_point][protocol][dest_addr]
					if not trace.trace_started:
						trace_dict_initalize_count[trace.trace_type] += 1

			print (vantage_point, trace_dict_initalize_count)

	def get_total_traceroutes_lasthop_analysis(self, _vantage_point_dic):

		print ("Format - type: [reply-received, diff-dest-reply, [diff-reply-domains]]")
		for vantage_point in _vantage_point_dic:

			trace_dict_initalize_count = {
			'http' : [0, 0, []],
			'tcp'  : [0, 0, []],
			'icmp' : [0, 0, []],
			'udp'  : [0, 0, []]
			}

			for dest_addr in _vantage_point_dic[vantage_point]['http'].keys():

				for protocol in trace_dict_initalize_count.keys():

					trace = _vantage_point_dic[vantage_point][protocol][dest_addr]

					if trace.trace_started and trace.reply_hop.reply_recv:
						trace_dict_initalize_count[trace.trace_type][0] += 1

						if not trace.dest_replied and verify_reponse_type(trace.reply_hop, trace.trace_type):
							trace_dict_initalize_count[trace.trace_type][1] += 1
							trace_dict_initalize_count[trace.trace_type][2].append(dest_addr)

			print (vantage_point, trace_dict_initalize_count)

	def compare_hops_for_n_hop_diff(self, _vantage_point_dic, n):

		for vantage_point in _vantage_point_dic:

			trace_dict_initalize_count = {
			'tcp'  : 0,
			'icmp' : 0,
			'udp'  : 0
			}
			
			for dest_addr in _vantage_point_dic[vantage_point]['http'].keys():

				http_trace = _vantage_point_dic[vantage_point]['http'][dest_addr]
				for protocol in trace_dict_initalize_count.keys():
					nontrace = _vantage_point_dic[vantage_point][protocol][dest_addr]

					if http_trace.path_length < nontrace.path_length - n and http_trace.trace_started:
						trace_dict_initalize_count[protocol] += 1

			print (vantage_point, trace_dict_initalize_count)

	def get_status_codes(self, _vantage_point_webpage_dict):

		for vantage_point in _vantage_point_webpage_dict:

			trace_dict_initalize_count = {
			'200' : 0,
			'300'  : 0,
			'400' : 0,
			'500'  : 0
			}

			for dest_addr in _vantage_point_webpage_dict[vantage_point].keys():

				webpage = _vantage_point_webpage_dict[vantage_point][dest_addr]

				if webpage.status_code:
					trace_dict_initalize_count[webpage.status_code] += 1

			print (vantage_point, trace_dict_initalize_count)

	def get_total_complete_webpages(self, _vantage_point_webpage_dict):

		complete = 0
		for vantage_point in _vantage_point_webpage_dict:

			for dest_addr in _vantage_point_webpage_dict[vantage_point].keys():

				webpage = _vantage_point_webpage_dict[vantage_point][dest_addr]

				if webpage.webpage_complete:
					complete += 1

			print (vantage_point, str(complete) + '/' + str(len(_vantage_point_webpage_dict[vantage_point].keys())))

	def replace_webpages_using_external_crawler(self, _vantage_point_webpage_dict):

		for vantage_point in _vantage_point_webpage_dict:

			for dest_addr in _vantage_point_webpage_dict[vantage_point].keys():

				_vantage_point_webpage_dict[vantage_point][dest_addr].replace_corrupt_page()

