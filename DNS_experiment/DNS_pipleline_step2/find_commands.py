import sys
with open("transfer_to_us_blocked_domains_with_ns.txt",'r') as file:
	data=file.read().split("\n")


def get_hex(domain):
	separate=domain.split(".")
	complete_hex=""
	for label in separate:
		length=hex(len(label))[2:]
		if len(length)==1:
			length="0"+length
		hex_of_label=''.join(x.encode('hex') for x in label)
		complete_hex=complete_hex+length+hex_of_label

	return "b77101200001000000000000"+complete_hex+"0000010001"

for one_domain_ip in data:
	if one_domain_ip=="":
		continue
	separate=one_domain_ip.split(" ")
	domain=separate[0]
	ip=separate[1]


	domain_in_hex=get_hex(domain)
	print domain_in_hex
	print domain
	new_command="tracelb -d 53 -p "+domain_in_hex+" -g 15 -H "+domain+" -P udp-sport "+ip
	print new_command
	with open("scamper_commands.txt",'a') as file:
		file.write(new_command+"\n")
	print "hey"

