import os
import sys
from multiprocessing import Process
os.chdir(os.path.dirname(sys.argv[0]))
import mydig
import time
domain_list=[]

with open("active_domains_set.txt",'r') as file:
	domain_list=file.read().split("\n")

def spread_work(domain_list,count):
	for domain in domain_list:
		print(domain)
		if domain=="":
			continue
		mydig.alias([count,domain,"A"])


N_THREADS = 60
 
	

THREAD_WORKLOAD = int(max(len(domain_list)/ N_THREADS, 1))
count=0
for thread_start_index in range(0, len(domain_list), THREAD_WORKLOAD):
    thread_chunk = domain_list[thread_start_index: thread_start_index + THREAD_WORKLOAD]
    for one_sharif_domain in thread_chunk:
    	with open(str(count)+"_shaarif_thread_domain",'a') as file:
    		file.write(one_sharif_domain+"\n")
    p = Process(target=spread_work, args=(thread_chunk,count,))
    count=count+1
    p.start()
