import matplotlib as plt


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

					trace = _vantage_point_dic[vantage_point][protocol][dest_addr][0]
					if not trace.trace_started:
						trace_dict_initalize_count[trace.trace_type] += 1

			print (vantage_point, trace_dict_initalize_count)
	

