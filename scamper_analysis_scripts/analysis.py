import threading
import thread
import utilities as ut

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

		print ("Format - protocol: [reply-received, diff-dest-reply, [diff-reply-domains]]")
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
						if trace.dest_replied: # reply from server in question
							trace_dict_initalize_count[trace.trace_type][0] += 1

						if not trace.dest_replied and ut.verify_reponse_type(trace.reply_hop, trace.trace_type):
							trace_dict_initalize_count[trace.trace_type][1] += 1
							trace_dict_initalize_count[trace.trace_type][2].append(dest_addr)

			print (vantage_point, trace_dict_initalize_count)

	def get_missing_hop_traceroutes_count(self, _vantage_point_dic, missing_count_threshold):

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
					missing_count = 0

					if trace.trace_started and trace.dest_replied:
						for hop in trace.path_hops:

							if not hop.reply_recv:
								missing_count += 1

								if missing_count == missing_count_threshold:
									trace_dict_initalize_count[protocol] += 1
									break
							else:
								missing_count = 0
			print (vantage_point, trace_dict_initalize_count)

	def get_missing_hop_icmp_plot(self, _vantage_point_dic):

		threshold = 2
		for vantage_point in _vantage_point_dic:

			missing_hops_dict = {}

			for dest_addr in _vantage_point_dic[vantage_point]['http'].keys():

				trace = _vantage_point_dic[vantage_point]['icmp'][dest_addr]
				missing_count = 0

				if trace.trace_started and trace.dest_replied:

					terminate = False
					for hop in trace.path_hops[::-1]:

						if not hop.reply_recv:
							missing_count += 1

							if missing_count >= threshold:
								terminate = True

						elif terminate:
							break

						else:
							missing_count = 0

					if missing_count < threshold:
						continue
						
					if missing_count in missing_hops_dict:
						missing_hops_dict[missing_count] += missing_count
					else:
						missing_hops_dict[missing_count] = missing_count

			missing_list = []
			keys = missing_hops_dict.keys()
			keys.sort()
			for key in keys:
				for i in [key] * missing_hops_dict[key]:
					missing_list.append(i)

			ut.plot_cdf(missing_list, "Number of Missing Hops", vantage_point + ": IMCP - Potential Hop Count Inflation")

	def compare_for_n_hop_diff_and_avg_pathlen(self, _vantage_point_dic, n, inverse):

		for vantage_point in _vantage_point_dic:

			trace_dict_initalize_count = {
			'tcp'  : [0, 0],
			'icmp' : [0, 0],
			'udp'  : [0, 0]
			}

			avg_http_pathlength = 0; http_count = 0;
			for dest_addr in _vantage_point_dic[vantage_point]['http'].keys():

				http_trace = _vantage_point_dic[vantage_point]['http'][dest_addr]
				for protocol in trace_dict_initalize_count.keys():
					nontrace = _vantage_point_dic[vantage_point][protocol][dest_addr]

					if not inverse and http_trace.path_length < (nontrace.path_length - n) and http_trace.trace_started:
						trace_dict_initalize_count[protocol][0] += 1
						trace_dict_initalize_count[protocol][1] += nontrace.path_length
						avg_http_pathlength += http_trace.path_length; http_count += 1

					elif inverse and http_trace.path_length > (nontrace.path_length + n) and http_trace.trace_started:
						trace_dict_initalize_count[protocol][0] += 1
						trace_dict_initalize_count[protocol][1] += nontrace.path_length
						avg_http_pathlength += http_trace.path_length; http_count += 1

			if trace_dict_initalize_count['tcp'][0]:
				trace_dict_initalize_count['tcp'][1] = trace_dict_initalize_count['tcp'][1] / float(trace_dict_initalize_count['tcp'][0])
			
			if trace_dict_initalize_count['icmp'][0]:
				trace_dict_initalize_count['icmp'][1] = trace_dict_initalize_count['icmp'][1] / float(trace_dict_initalize_count['icmp'][0])
			
			if trace_dict_initalize_count['udp'][0]:
				trace_dict_initalize_count['udp'][1] = trace_dict_initalize_count['udp'][1] / float(trace_dict_initalize_count['udp'][0])
			
			if http_count:
				avg_http_pathlength = avg_http_pathlength/float(http_count)

			print ("Format - protocol : [count, average-path-length]")
			print (vantage_point, trace_dict_initalize_count)
			print (vantage_point, 'HTTP', avg_http_pathlength)

	def icmp_shorter_path_length_analysis(self, _vantage_point_dic): # Path length must be complete

		for vantage_point in _vantage_point_dic:

			trace_reasons_dict = {
				'1': 0, # When server replies after a certain TTL value
				'2': 0, # Server itself or the server network blocking ICMP packets
				'3': [0, 0], # When icmp paths follow a completely different path: (count, average diverging hop number)
				'4': 0 # ICMP error codes
			}
			
			for domain in _vantage_point_dic[vantage_point]['http'].keys():

				http_trace = _vantage_point_dic[vantage_point]['http'][domain]
				icmp_trace = _vantage_point_dic[vantage_point]['icmp'][domain]

				if http_trace.trace_started and http_trace.path_length > icmp_trace.path_length and icmp_trace.reply_hop.reply_recv:

					diverging_hop_num = ut.compare_path_similiarity(icmp_trace.path_hops, http_trace.path_hops)

					if ut.compare_hops(http_trace.path_hops[http_trace.path_length - 1].reply_addrs, http_trace.path_hops[http_trace.path_length - 2].reply_addrs):
						trace_reasons_dict['1'] += 1

					elif http_trace.reply_hop.reply_recv and not icmp_trace.reply_hop.reply_recv:
						trace_reasons_dict['2'] += 1

					elif ut.detect_icmp_error_code(icmp_trace):
						trace_reasons_dict['4'] += 1

					elif (diverging_hop_num) != -1:

						trace_reasons_dict['3'][0] += 1
						trace_reasons_dict['3'][1] += diverging_hop_num

					else:
						print ("Case not handled %s" % domain)

			trace_reasons_dict['3'][1] = trace_reasons_dict['3'][1] / float(trace_reasons_dict['3'][0])
			print (vantage_point, trace_reasons_dict)

	def get_icmp_lasthop_subnet_analysis(self, _vantage_point_dic):

		for vantage_point in _vantage_point_dic:

			icmp_subnet_dict = {}
			overlap_list = []

			for dest_addr in _vantage_point_dic[vantage_point]['http'].keys():

				icmp_trace = _vantage_point_dic[vantage_point]['icmp'][dest_addr]
				last_responsive_hop_ip = icmp_trace.path_hops[icmp_trace.path_length - 1].reply_addrs[0]
				dest_ip = icmp_trace.dest_addr

				if icmp_trace.trace_started and not icmp_trace.reply_hop.reply_recv:

					overlap = ut.compute_subnet_overlap(last_responsive_hop_ip, dest_ip)

					if overlap in icmp_subnet_dict:
						icmp_subnet_dict[overlap] += 1
					else:
						icmp_subnet_dict[overlap] = 1	

			keys = icmp_subnet_dict.keys()
			keys.sort()
			for key in keys:
				for i in [key] * icmp_subnet_dict[key]:
					overlap_list.append(i)

			ut.plot_cdf(overlap_list, "Subnet Mask /n", vantage_point + ": IMCP - Subnet Overlap of Destination IP and Last Responsive IP")

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

				if webpage.webpage_complete: # TODO: Add external crawler webpage count as well
					complete += 1

			print (vantage_point, str(complete) + '/' + str(len(_vantage_point_webpage_dict[vantage_point].keys())))

	def threaded_webpage_replacement(self, vantage_point , _vantage_point_webpage_dict, domain_chunk):
		
		for dest_addr in domain_chunk:

			_vantage_point_webpage_dict[vantage_point][dest_addr].replace_corrupt_page()

	def replace_webpages_using_external_crawler(self, _vantage_point_webpage_dict):

		for vantage_point in _vantage_point_webpage_dict:

			threads_list = []
			# for dest_addr in _vantage_point_webpage_dict[vantage_point].keys():

			# 	_vantage_point_webpage_dict[vantage_point][dest_addr].replace_corrupt_page()

			for start_chunk in range(0, len(_vantage_point_webpage_dict[vantage_point].keys()), 50):
				domain_chunk = _vantage_point_webpage_dict[vantage_point].keys()[start_chunk: start_chunk + 50]

				child = threading.Thread(target = self.threaded_webpage_replacement, args = (vantage_point, _vantage_point_webpage_dict, domain_chunk,))
				child.start()

				threads_list.append(child)

			for t in threads_list:
				t.join()

