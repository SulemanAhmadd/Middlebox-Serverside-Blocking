"""
    Run as:
        python dns_tr_parser.py input_log_filename input_file_with_pairs

    for example:
        python dns_tr_parser.py final_log input_pairs.txt
"""

import sys
import os
import pprint
import re
import collections
import seaborn as sns
import matplotlib.pyplot as plt

def get_traces(input_log_fn):
    all_traces = []
    with open(input_log_fn,'r') as input_log_obj:
        new_trace = []
        for line in input_log_obj:
            line = line.strip()
            if "MDA DNS" in line:
                new_trace = filter(None, new_trace)
                all_traces.append(new_trace)
                new_trace = []
                new_trace.append(line)
            else:
                new_trace.append(line)
        new_trace = filter(None, new_trace)
        all_traces.append(new_trace)
        all_traces = filter(None, all_traces)
        return all_traces

def get_pairs(input_pairs_fn):
    all_pairs = []
    with open(input_pairs_fn,'r') as input_pairs_obj:
        for line in input_pairs_obj:
            line = line.strip()
            line_eles = line.split('\t')
            dom = line_eles[0]
            input_ip = line_eles[1]
            input_server_ip = line_eles[2]
            tup = (dom, input_ip, input_server_ip)
            all_pairs.append(tup)
    return all_pairs

def get_traces_sv(all_traces, input_server_ip):
    rel_traces = []
    for trace in all_traces:
        first_line = trace[0]
        strt_ind = first_line.find('to') + 3
        end_ind = first_line.find(',')
        trace_serv_ip = first_line[strt_ind:end_ind]
        if trace_serv_ip == input_server_ip:
            rel_traces.append(trace)
    return rel_traces

def get_source_ip(line):
    ind = line.find('-')
    line = line[ind+1:]
    strt_ind = line.find('-') + 3
    end_ind = line.find('to') - 1
    src_ip = line[strt_ind:end_ind]
    return src_ip

def parse_trace(my_trace):
    first_line = my_trace[0]
    last_line = my_trace[-1]
    src_ip = get_source_ip(first_line)
    my_trace = my_trace[1:]
    if "ICMP response of server" in first_line:
        all_dicts = []
        for line in my_trace:
            interfaces_in_line = re.split("->", line)
            interfaces_in_line.reverse()
            for idx, interface in enumerate(interfaces_in_line):
                try:
                    next_inf = interfaces_in_line[idx+1]
                    interface = interface.strip(' ')
                    next_inf = next_inf.strip()
                    my_dict = {}
                    my_dict[interface] = next_inf
                    all_dicts.append(my_dict)
                except:
                    pass
        return "ICMP", '', src_ip, all_dicts
    elif "DNS response of server" in first_line:
        my_trace = my_trace[:-1]
        all_dicts = []
        for line in my_trace:
            interfaces_in_line = re.split("->", line)
            interfaces_in_line.reverse()
            for idx, interface in enumerate(interfaces_in_line):
                try:
                    next_inf = interfaces_in_line[idx+1]
                    interface = interface.strip(' ')
                    next_inf = next_inf.strip()
                    my_dict = {}
                    if not(interface is '*' and next_inf is '*'):
                        my_dict[interface] = next_inf
                        all_dicts.append(my_dict)
                except:
                    pass
        serv_ttl = last_line[0:last_line.find(' ')]
        return "DNS", serv_ttl, src_ip, all_dicts

def get_ttl(input_ip, trace_dicts):
    ttl = 0
    new_src = input_ip
    go_on = True
    while go_on:
        go_on = False
        for dct in trace_dicts:
            try:
                new_src = dct[new_src]
                ttl += 1
                go_on = True
                break
            except:
                pass
    return str(ttl)

def get_ttl_from_trace(flag, serv_ttl, src_ip, dst_ip, trace_dicts, input_ip):
    input_ip_ttl = get_ttl(input_ip, trace_dicts)
    #
    if input_ip_ttl == '0':
        return 'prox_failed'
    #
    serv_fl_ttl = ''
    if flag is "DNS":
        serv_fl_ttl = serv_ttl
    elif flag is "ICMP":
        serv_fl_ttl = get_ttl(dst_ip, trace_dicts)
    #
    if '.' in serv_ttl:
        return 'prox_failed_serv'
    #
    results_string = "\n-------------------------------------------------------------------\n"
    results_string += "From the file " + sys.argv[1] + ', analysis was done on the trace with destination IP ' + dst_ip
    results_string += "\n*** " + flag + ' case ***'
    results_string += "\nTTL for the input IP \'" + input_ip + "\': " + input_ip_ttl
    results_string += "\nTTL for the server (destination IP) \'" + dst_ip + "\': " + str(serv_fl_ttl)
    results_string += "\n-------------------------------------------------------------------\n"

    print(results_string)
    with open('results.out','a') as results_obj:
        results_obj.write(results_string)

    return int(serv_fl_ttl) - int(input_ip_ttl)

def make_bar_graph(frequencies):
    my_dict = dict(frequencies)
    if my_dict == {}:
        return
    data_inp = {}
    data_inp["ttl_difs"] = my_dict.keys()
    data_inp["frequencies"] = my_dict.values()
    sns.set(style="darkgrid")
    plt.figure(dpi=300)
    ax = sns.barplot(x="ttl_difs",y="frequencies",data=data_inp)
    ax.set(xlabel='TTL difference', ylabel='Frequency')
    fig = ax.get_figure()
    fig.savefig('ttl_diff.png')

def make_summary_file(all_ttl_diff):
    frequencies = collections.Counter(all_ttl_diff)
    with open('summary.out','w') as summary_obj:
        summary_obj.write('Diff b/w IP & Server \t\t\t Frequency\n')
        for ttl_diff in frequencies:
            summary_obj.write(str(ttl_diff) + '\t\t\t' + str(frequencies[ttl_diff]) + '\n')
    make_bar_graph(frequencies)

def write_to_prox(domain, input_ip, input_server_ip):
    with open('proximity_test_passed','a') as prox_out:
        prox_out.write(domain + '\t' + input_ip + '\t' + input_server_ip + '\n')

if __name__ == "__main__":
    input_log_fn = sys.argv[1]
    input_pairs_fn = sys.argv[2]

    all_traces = get_traces(input_log_fn)
    all_pairs = get_pairs(input_pairs_fn)

    try:
        os.remove('proximity_test_passed')
        os.remove('results.out')
        os.remove('summary.out')
    except:
        pass

    all_ttl_diff = []
    for domain, input_ip, input_server_ip in all_pairs:
        my_traces = get_traces_sv(all_traces, input_server_ip)
        if my_traces == []:
            out_str = domain + '\t' + 'No relevant trace(s) for destination IP ' + input_server_ip
            print(out_str)
            print('-------------------------------------------------------------------')
            with open('results.out','a') as results_obj:
                results_obj.write(out_str + '\n')
            continue
        for each_trace in my_traces:
            flag, serv_ttl, src_ip, trace_dicts = parse_trace(each_trace)
            ttl_diff = get_ttl_from_trace(flag, serv_ttl, src_ip, input_server_ip, trace_dicts, input_ip)
            if ttl_diff == 'prox_failed':
                out_str = domain + '\t' + "Input IP not in trace"
                print(out_str)
                print('-------------------------------------------------------------------')
                with open('results.out','a') as results_obj:
                    results_obj.write(out_str + '\n')
                continue
            elif ttl_diff == 'prox_failed_serv':
                out_str = domain + '\t' + "Server IP not in trace - TTL for server could not be found"
                print(out_str)
                print('-------------------------------------------------------------------')
                with open('results.out','a') as results_obj:
                    results_obj.write(out_str + '\n')
                #
                write_to_prox(domain, input_ip, input_server_ip)
                #
                continue
            all_ttl_diff.append(ttl_diff)

    make_summary_file(all_ttl_diff)
