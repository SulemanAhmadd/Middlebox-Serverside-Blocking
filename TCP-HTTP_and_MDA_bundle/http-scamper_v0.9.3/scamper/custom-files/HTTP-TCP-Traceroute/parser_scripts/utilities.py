import numpy as np
import matplotlib.pyplot as plt

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

def detect_icmp_error_code(icmp_trace):
	if not icmp_trace.reply_hop.reply_recv:
		return False

	reply_addrs = icmp_trace.reply_hop.reply_addrs
	reply_resps = icmp_trace.reply_hop.dest_resps

	for reply in reply_addrs:

		for resp in reply_resps[reply]:

			if '!' in resp:
				return True

	return False

def compare_hops(hoplast, hop2last):

	if not len(hop2last) or not len(hoplast):
		return False

	bigger = None; smaller = None;
	if len(hoplast) >= len(hop2last):
		smaller = hop2last
		bigger = hoplast
	else:
		smaller = hoplast
		bigger = hop2last

	for ip in range(len(smaller)):
		if smaller[ip] not in bigger:
			return False

	return True

def compare_path_similiarity(trace1_hops, trace2_hops):

	count = 0
	if len(trace1_hops) >= len(trace2_hops):
		count = len(trace2_hops)
	else:
		count = len(trace1_hops)

	for hop_index in range(count):
		if not trace1_hops[hop_index].reply_addrs and not trace2_hops[hop_index].reply_addrs:
			continue

		if not compare_hops(trace1_hops[hop_index].reply_addrs, trace2_hops[hop_index].reply_addrs):
			return hop_index + 1

	return -1

def ipstring_to_ipbin(ip):

    ip = ip.split(".")
    ret_binary = ""

    for part in ip:

        part = int(part)
        bin_part =  '0'*(8-len(bin(part)[2:]))+bin(part)[2:]
        ret_binary = ret_binary + bin_part

    return ret_binary

def generate_subnet_mask(length):

    return '1'*(length)+'0'*(32-length)

def apply_mask(ip, subnet_mask):

    ip = int(ip,2)
    subnet_mask = int(subnet_mask,2)
    int_representation = ip&subnet_mask

    return '0'*(32-len(bin(int_representation)[2:]))+bin(int_representation)[2:]

def ipbin_to_ipstring(ip):

    ret_string = []

    for x in xrange(0,32,8):
        ret_string.append(str(int(ip[x:x+8],2)))

    return ".".join(ret_string)

def compute_subnet_overlap(ip1, ip2):

	for subnet_val in reversed(range(0, 33)):

		subnet1 = ipbin_to_ipstring( apply_mask(ipstring_to_ipbin(ip1), generate_subnet_mask(subnet_val)) )
		subnet2 = ipbin_to_ipstring( apply_mask(ipstring_to_ipbin(ip2), generate_subnet_mask(subnet_val)) )

		if subnet2 == subnet1:
			return subnet_val

def make_cdf(data_list):

    x = np.sort(data_list)
    y = np.arange(len(x))/float(len(x))
    return x,y

def plot_cdf(data, x_label, title):

    x, y = make_cdf(data)
    plt.xlabel(x_label)
    plt.ylabel("CDF")
    plt.xticks(x, x)
    plt.title(title)
    plt.plot(x, y)
    plt.show()

def write_to_file(filename, domain, ip):
	
	filename = 'incomplete-icmp-' + filename + '.txt'

	with open(filename, 'a+') as file:
		file.write(domain + ' ' + ip + ',' + '\n')

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