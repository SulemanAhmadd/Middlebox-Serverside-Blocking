import subprocess
import threading
import thread
import time
import sys 
import os

def parse_input_line(line):
	line = line.strip().split()
	domain = line[0].strip(',')
	ip = line[1].strip(',')

	return domain, ip

def main():
	input_filename = sys.argv[1]

	unique_ips = set()

	inputfile = open(input_filename, "r")
	inputlist = inputfile.readlines()
	inputfile.close()

	count = 0

	with open('scamper-input-dns.txt', 'a+') as outfile:
		for dest_addr in inputlist:

			domain, ip = parse_input_line(dest_addr)

			if ip not in unique_ips:
				outfile.write('trace -P UDP-Paris -p 34ef010000010000000000000756455253494f4e0442494e440000100003 -d 53 %s\n' % ip)
				outfile.write('trace -P ICMP-paris %s\n' % (ip))
				count += 1

			unique_ips.add(ip)

	os.system("./run-dns-scamper.sh dns-scamper-results.txt scamper-input-dns.txt")

if __name__ == '__main__':

	if len(sys.argv) != 2:
		print("Usage: python run-exp.py [input-list]")
	else:
		main()