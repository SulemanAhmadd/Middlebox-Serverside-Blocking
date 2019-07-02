import re

class Hop(object):

    def __init__(self):
        self.reply_addrs = []           # reply ip address
        self.dest_resps = {}            # {ip_addr : [resp flags]}
        self.reply_recv = True          # * or ip address

    def parse_hop_string(self, hop_str):
        pattern = re.compile(r'[0-9]+(?:\.[0-9]+){3}')
        for ele in hop_str:
            if pattern.match(ele):
                self.reply_addrs.append(ele)

        if not self.reply_addrs:
            self.reply_recv = False
            return

        for index, ip_addr in enumerate(self.reply_addrs):
            start_index = hop_str.index(ip_addr)
            end_index = index + 1

            if end_index >= len(self.reply_addrs):
                end_index = len(hop_str)
            else:
                end_index = hop_str.index(self.reply_addrs[end_index])

            self.parse_resp_type(ip_addr, hop_str[start_index:end_index])

    def parse_resp_type(self, ip_addr, response):
        capture = False; packet = []; resp_pkts = []
        for resp_flag in response:
            resp_flag = resp_flag.strip(',').strip(']').strip('[')

            if 'ms' in resp_flag and not capture:
                capture = True; continue;
            elif 'ms' in resp_flag and capture:
                resp_pkts.append("-".join(packet[:-1]))
                packet = []; continue;

            if capture:
                packet.append(resp_flag)

        resp_pkts.append("-".join(packet))
        self.dest_resps[ip_addr] = resp_pkts


    def p_print(self):
        if not self.reply_recv:
            print ('None')

        for addr in self.reply_addrs:
            print("%s : %s" % (addr, self.dest_resps[addr]))

class Trace(object):

    def __init__(self, _trace_type, _trace):
        # Header Fields
        self.src_addr = ""              # source ip address     
        self.dest_addr = ""             # destination ip address
        self.domain_name = ""           # domain name of dest (can be multiple due to cdns)

        # Path Fields
        self.path_hops = []             # list of hop objects in trace
        self.path_length = 0            # total hop count of trace

        # Reply Fields
        self.dest_replied = False       # if destination ip replied or not
        self.reply_hop = None           # last hop that replied
        self.trace_started = False      # if trace initialized (syn ack recv in case of http)

        # Trace Fields
        self.trace_type = _trace_type    #  (http, icmp, udp, tcp)
        self.parse_trace(_trace)

    def parse_trace(self, trace):
        
        header = trace[0]
        self.src_addr = header[2]
        self.dest_addr = header[4]

        if self.trace_type == 'http':
            self.domain_name = header[5]

        routes = trace[1:]

        self.parse_hops(routes)
        self.path_length = len(routes)

        if not self.path_length:
            return

        for hop in reversed(self.path_hops):
            if hop.reply_recv:
                break
            self.path_length -= 1

        self.trace_started = True
        self.reply_hop = self.path_hops[-1]

        if self.dest_addr in self.reply_hop.reply_addrs:
            self.dest_replied = True

            if self.trace_type == 'udp':
                udp_resp = self.reply_hop.dest_resps[self.dest_addr]
                udp_resp.append('UDP')
                self.reply_hop.dest_resps[self.dest_addr] = filter(None, udp_resp)

    def parse_hops(self, routes):
        
        for route in routes:
            hop = Hop()
            hop.parse_hop_string(route)

            self.path_hops.append(hop)

    def get_destination(self):
        return self.domain_name

    def p_print(self):
        print ("*****************************************************************************")
        print ("Trace Type       : %s" % self.trace_type)
        print ("Source Addr      : %s" % self.src_addr)
        print ("Destination Addr : %s" % self.dest_addr)
        print ("Domain Name      : %s" % self.domain_name)
        print ("Trace Length     : %d" % self.path_length)
        print ("Trace Started    : %r" % self.trace_started)
        print ("Dest Replied     : %r" % self.dest_replied)
        
        print ("Hops ...")
        hop_count = 1
        for hop in self.path_hops:
            print ("-----------%d-----------" % (hop_count))
            hop.p_print()
            hop_count += 1
        print ("*****************************************************************************")