import os
import sys
os.chdir(os.path.dirname(sys.argv[0]))
from subprocess import check_output
import subprocess
import re


with open("have_auth_no_ip_extended.common_three_runs.txt",'r') as file:
	arr=file.read().split("\n")
count=0
pass #print len(arr)
pass #print arr
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
	pass #print "Domain ",domain
	#sys.exit()
	pass #print "This is the filter : ",complete_filter
	pass #print "before ip ",i
	#i=i[:-1]
	pass #print "after ip ",i,"\n\n"
	os.system("tshark -r MDA_DNS_tcpdump_logs.pcap -w"+" ./traces/"+ip+".pcap -F pcap ip.addr=="+ip)
	count=count+1
	pass #print count



pass #print count



