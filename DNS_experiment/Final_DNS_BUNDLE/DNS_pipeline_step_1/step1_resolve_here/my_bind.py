from multiprocessing import Process
import dns.resolver
from dns.resolver import NoAnswer
from dns.resolver import NXDOMAIN
from dns.resolver import NoNameservers
import os
import sys
sys.path.insert(0, '/root')
os.chdir(os.path.dirname(sys.argv[0]))
import time


def one_fun(my_list,num):
	res = dns.resolver.Resolver(configure=False)
	print("I am thread ",num)
	print("my domains",my_list)
	num=str(num)
	start=time.time()
	res.nameservers = ["127.0.0.1"]

	domain_list=my_list
	fail_domain=[]

#	with open("top_tenth_million.txt",'r') as file:
#		domain_list=file.read().split("\n")
	retry=0
	count=0
	for i in range(2):
		fail_str=""
		print("stopppppppppp index\n",i)
		for domain in domain_list:
			print("Thread num ",num,"count of sites ",count," Time elapsed ",(time.time()-start))
			count=count+1
			

			try:
				resultDNS= res.query(domain, 'a')
				with open(num+"_success.txt",'a') as file1:
						file1.write(str(domain)+" ")
				for i in resultDNS:
					print("google's ans: " + str(i))
					with open(num+"_success.txt",'a') as file1:
						file1.write(str(i)+",")
				answer=''
				# for item in resultDNS:
				# 	resultant_str = ','.join([str(item), answer])
				with open(num+"_success.txt",'a') as file1:
					file1.write("\n")
				print(num," pass ",domain)
			

			except Exception as e:
				fail_str=fail_str+domain+" "+str(e)+"\n"
				print(num," Fail ",domain)
				fail_domain.append(domain)
		domain_list=fail_domain
		fail_domain=[]



	with open(num+"_fail.txt",'w') as file1:
					file1.write(fail_str)
	print("total time ")
	print(time.time()-start)
	print("length of fails",len(fail_domain))
	with open("time.txt",'a') as file5:
		file5.write("Thread : "+num+" Time taken "+str(time.time()-start)+" failures "+str(len(fail_domain))+"\n")

	


N_THREADS = 100
 
domain_list=[]
	

with open("alexa.txt",'r') as file:
	domain_list=file.read().split("\n")
THREAD_WORKLOAD = int(max(len(domain_list)/ N_THREADS, 1))
count=0
for thread_start_index in range(0, len(domain_list), THREAD_WORKLOAD):
	thread_chunk = domain_list[thread_start_index: thread_start_index + THREAD_WORKLOAD]
	p = Process(target=one_fun, args=(thread_chunk,count,))
	count=count+1
	p.start()


 
