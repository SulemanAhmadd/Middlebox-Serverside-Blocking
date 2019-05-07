import os

all_files = os.listdir('../step4_traceroute')
tracefiles = []
for file in all_files:
    if "_dnstraceroute_" in file:
        tracefiles.append('../step4_traceroute/' + file)

try:
    os.remove('../step4_traceroute/failed_dns_tr.txt')
except:
    pass

for tracefile in tracefiles:
    dom_name = tracefile[tracefile.find('e/')+2:tracefile.find('_dns')]
    last_line = ''
    with open(tracefile, 'r') as file_obj:
        for line in file_obj:
            last_line = line.strip()
        line_eles = last_line.split(' ')
        last_responding_ip = line_eles[-3]
        server_ip = line_eles[-2]
        if (not(last_responding_ip is server_ip)) or (line_eles[-1] is 'ICMP'):
            with open('../step4_traceroute/failed_dns_tr.txt', 'a') as file_obj:
                file_obj.write(dom_name + '\t' + last_responding_ip + '\t' + server_ip + '\n')
