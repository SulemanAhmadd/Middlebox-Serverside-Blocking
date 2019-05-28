import os
import sys
os.chdir(os.path.dirname(sys.argv[0]))
from subprocess import check_output
import subprocess
import re


with open("transfer_to_us_blocked_domains_with_ns.txt",'r') as file:
	arr=file.read().split("\n")
count=0
print len(arr)
print arr
for i in arr:
	separate=i.split(" ")
	if i=="":
		continue
	domain=separate[0]
	ip=separate[1]
	filter_part="udp matches "
	complete_filter=""
	labels=domain.split(".")
	for one_label in labels:
		complete_filter=complete_filter+one_label+"."
#	complete_filter=complete_filter[:-5]
	complete_filter=filter_part+"\""+complete_filter+"\""
	print "Domain ",domain
	#sys.exit()
	print "This is the filter : ",complete_filter
	print "before ip ",i
	#i=i[:-1]
	print "after ip ",i,"\n\n"
	os.system("tshark -r MDA_DNS_tcpdump_logs.pcap -w"+" ./traces/"+ip+".pcap -F pcap ip.addr=="+ip)
	count=count+1
	print count



print count



