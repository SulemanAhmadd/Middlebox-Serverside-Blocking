import mydig
import time
domain_list=[]

with open("result.txt",'r') as file:
	domain_list=file.read().split("\n")

start_time=time.time()
for domain in domain_list:
	print(domain)
	mydig.alias(["junk",domain,"A"])

total=time.time()-start_time
print("\nTotal time taken : "+str(total))
