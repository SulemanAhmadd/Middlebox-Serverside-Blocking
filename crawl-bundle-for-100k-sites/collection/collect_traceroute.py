"""

    Run as:
        sudo python3 collect_traceroute.py domain_list_file

    Note: requires root privileges due to scapy

    Also requires disabling the outgoing RSTs. On Linux this can be done as:
        iptables -l OUTPUT -p tcp --tcp-flags ALL RST,ACK -j DROP

"""

from scapy.all import *
from random import randint
from scapy.layers import *
import threading
import thread

def get_packet_type(packet):
    """
        Returns the type of received packet
       
        ICMP:                 ICMP
        TCP-Empty-[flags]:    No payload
        TCP-HTTP-[flags]:     HTTP payload
        TCP-Non_HTTP-[flags]: Non-HTTP payload
    """
    
    if isinstance(packet.payload, ICMP):
        return "ICMP"
    elif isinstance(packet.payload, TCP):
        if len(packet.payload[TCP].payload) == 0:
            return "TCP-Empty-" + str(packet.payload[TCP].flags)
        elif "HTTP" in str(packet.payload[TCP].payload).split("\n")[0]: 
            return "TCP-HTTP-" + str(packet.payload[TCP].flags) 
        else:
            print(packet.payload[TCP].payload.show())
            return "TCP-NonHTTP-" + str(packet.payload[TCP].flags)
    else:
        return "-"


def get_packet_content(packet, packet_type):
    """
        Returns squeezed TCP payloads 
    """
    if "TCP" in packet_type:
        packet_content = packet.payload[TCP].payload
        if packet_content:
            squeezed_packet_content = packet_content.strip("\n")
            return squeezed_packet_content
    return str(None)


def has_HTTP_layer(resp_packets):
    for packet in resp_packets:
        # this check is required because an ICMP packet may contain the
        # original HTTP packet, passing the HTTP layer check
        if packet[1].haslayer(ICMP):
            continue
        elif packet[1].haslayer("HTTP"):
            #packet[1].show()
            return True
        else:
            continue
    return False


def do_icmp_traceroute(dest):
    """
        Sends an ICMP echo packet with increasing TTLs
    """
    ans, unans = sr(IP(dst = dest, 
                       ttl = (1,25),
                       id  = randint(0,10000))/
                    ICMP(), 
                    timeout = 20)

    out_file = "_".join([dest, "icmptraceroute", ".txt"])
    with open(out_file, "w") as f:
        for snd,rcv in ans:
            f.write(str(snd.ttl) + " " + rcv.src + " " + snd.dst + " " + \
                    get_packet_type(rcv) + "\n")
     

def do_tcp_traceroute(dest):
    """
        Sends a SYN packet with increasing TTLs
    """
    ans, unans = sr(IP(dst = dest, 
                       ttl = (1,25),
                       id  = randint(0,10000))/
                    TCP(sport = randint(10000,20000), 
                        dport = 80, 
                        flags = "S"), 
                    timeout = 20)

    out_file = "_".join([dest, "tcptraceroute", ".txt"])
    with open(out_file, "w") as f:
        for snd,rcv in ans:
            f.write(str(snd.ttl) + " " + rcv.src + " " + snd.dst + " " + \
                    get_packet_type(rcv) + "\n")


def do_http_traceroute(dest):
    """
        First establishes a connection with the intended destination, by
        sending a SYN and receiving a SYN-ACK. Then sends an HTTP request with
        increasing TTLs
    """
    IPL = IP(dst = dest)
    out_file = "_".join([dest, "httptraceroute", ".txt"])
    response_strings = []

    for ttl in range(1, 25):
        source_port = randint(10000,20000)
        TCP_SYN = TCP(sport = source_port, 
                      dport = 80, 
                      flags = "S", 
                      seq = randint(20000,80000))

        '''
            Attempt to get a SYN-ACK from the intended destination
        '''
        N_SYN_ACK_TRIES = 3
        got_syn_ack = False

        for attempt in range(0, N_SYN_ACK_TRIES):
            TCP_SYNACK = sr1(IPL/TCP_SYN, 
                             timeout = 15)

            if not TCP_SYNACK or not isinstance(TCP_SYNACK.payload, TCP): 
                continue
            else:
                got_syn_ack = True
                break

        if not got_syn_ack:
            raise Exception("No SYN-ACK received")

        '''
        Set up the ACK packet with the HTTP request and the correct TTL value"
        '''
        ack_number = TCP_SYNACK.seq + 1
        IP_w_TTL=IP(dst = dest, ttl=ttl)
        TCP_ACK = TCP(sport = source_port, 
                      dport = 80, 
                      flags = "PA", 
                      seq = TCP_SYN.seq + 1, 
                      ack = ack_number)
        HTTP_request_str = "GET / HTTP/1.1\r\nHost: " + dest + "\r\nUser-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0\r\nAccept-Language: en-US,en;q=0.5\r\nConnection: keep-alive\r\nUpgrade-Insecure-Requests: 1\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nAccept-Encoding:gzip, deflate\r\n\r\n"
        HTTP_request = IP_w_TTL/TCP_ACK/HTTP_request_str

        HTTP_response, error = sr(HTTP_request, 
                                  timeout = 15, 
                                  multi = True)

        for snd,rcv in HTTP_response: 
            response_strings.append(str(snd.ttl) + " " + rcv.src + " " +
                                    snd.dst + " " + get_packet_type(rcv) + "\n")
                                    #+ " " + get_packet_content(rcv, get_packet_type(rcv)) + "\n")

    with open(out_file, "w") as f:
        for resp in response_strings:
            f.write(resp)


def do_all_traceroutes(domain_list):
    """
        Attempt ICMP, TCP, and HTTP traceroutes for the given domain list
    """
    print "My work is to traceroute this list", domain_list
    for dest in domain_list:
        try:
            do_icmp_traceroute(dest)
            do_tcp_traceroute(dest)
            do_http_traceroute(dest)
        except Exception as ex:
            with open("failed_traceroutes.txt",'a') as f:
                f.write(dest + "\t" + str(type(ex).__name__) + "\tDetails: " + str(ex) + "\n")
    

if __name__ == "__main__":
    domain_list = list()
    N_THREADS = 2
     
    with open(sys.argv[1]) as f:
        for line in f:
            domain_list.append(line.strip())

    THREAD_WORKLOAD = max(len(domain_list)/ N_THREADS, 1)

    for thread_start_index in range(0, len(domain_list), THREAD_WORKLOAD):
        thread_chunk = domain_list[thread_start_index: thread_start_index + THREAD_WORKLOAD]
        child = threading.Thread(target = do_all_traceroutes, 
                                 args = (thread_chunk,))
        child.start()
