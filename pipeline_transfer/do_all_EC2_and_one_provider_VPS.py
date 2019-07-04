import os
import time
import sys

PATH_TO_CONFIG_FILES_ON_LOCAL_COMP = "/Users/mjav/LUMS/research/tracerouter/SSB/nord_vpn_config_files/"

VP_IP_map = {
				"US" : "34.211.104.1",
				#"Russia": "91.218.115.15",
				"Turkey": "34.217.144.157",
				"UK": "35.165.118.6",
				"Japan": "34.219.77.94",
				"HongKong": "34.218.235.186",
				"Australia": "34.217.11.84",
				"Germany" : "34.212.25.104",
				"SA": "52.36.78.35",
				 #"PK": "203.135.63.20"}
			}

VP_private_IP_map = {  
						"US":  "172.31.41.6",
						"Turkey": "172.31.39.244",
						"UK": "172.31.32.24",
						"Japan": "172.31.32.31",
						"HongKong": "172.31.32.247",
						"Australia": "172.31.46.74",
						"Germany": "172.31.34.228",
						"SA": "172.31.33.241"
					}


# Note: these files have been fixed using:
# sed -i .wo-auth-fix -e 's/auth-user-pass/auth-user-pass auth.txt/g' *
VP_NordVPN_config_map = {"US" : "us2124.nordvpn.com.udp.ovpn",
						#"Russia": "91.218.115.15",
						"Turkey": "tr14.nordvpn.com.udp.ovpn",
						"UK": "uk1062.nordvpn.com.udp.ovpn",
						"Japan": "jp176.nordvpn.com.udp.ovpn",
						"HongKong": "hk55.nordvpn.com.udp.ovpn",
						"Australia": "au232.nordvpn.com.udp.ovpn",
						"Germany" : "de527.nordvpn.com.udp.ovpn",
						"SA": "za10.nordvpn.com.udp.ovpn",
						 #"PK": "203.135.63.20"}
						}

 
def set_up_vpn():
	for VP in VP_IP_map:
	#	 if VP in ["Turkey", "Australia"]:
	#		continue

		 print "Setting up VPN for VP ", VP
		 # copy the config file
		 os.system("scp -i ~/.ssh/2b-proxy.pem " + PATH_TO_CONFIG_FILES_ON_LOCAL_COMP +  VP_NordVPN_config_map[VP] + \
				  " ubuntu@"  + VP_IP_map[VP] + ":~/NordVPN")

		 # edit the route config
		 fix_route_config = "sed -e s/172.31.32.31/" + VP_private_IP_map[VP] + "/g -i route_config.sh"

		 # point to the right config file
		 fix_vpn_file = "sed -e s/de527.nordvpn.com.udp.ovpn/" + VP_NordVPN_config_map[VP] + "/g -i start_vpn.sh"
		 os.system("""ssh -i ~/.ssh/2b-proxy.pem ubuntu@""" + VP_IP_map[VP] + """ \
			   "bash -c 'cd ~/NordVPN/;""" + fix_route_config + "; " + \
			   fix_vpn_file + """;'" """)

		 # start the VPN
		 os.system("""ssh -i ~/.ssh/2b-proxy.pem ubuntu@""" + VP_IP_map[VP] + """ "screen -m -d bash -c 'cd ~/NordVPN/; bash start_vpn.sh;'" """)
  

def start_vpn(): 
	for VP in VP_IP_map:
		if VP in []:
			continue

		print "Starting VPN for", VP

		# First kill any existing vpn process
		os.system("""ssh -i ~/.ssh/2b-proxy.pem ubuntu@""" + VP_IP_map[VP] + """ "bash -c 'sudo pkill -f openvpn;'" """)

		os.system("""ssh -i ~/.ssh/2b-proxy.pem ubuntu@""" + VP_IP_map[VP] + """ "screen -m -d bash -c 'cd ~/NordVPN/; bash start_vpn.sh;'" """)

def transfer_bundle_to_all_machines(vp_ip,vp_bundle_name,SSH_KEY_PATH,USERNAME,vp_name):
   
	print "Starting data transfer for VP whose name is ", vp_name

	# Here we are transfering bundle to relevant EC2 machines and cleaning old directories
	 
	os.system("scp -i " + SSH_KEY_PATH + " -r " + vp_bundle_name +" "+ USERNAME+"@"\
		  + vp_ip + ":~/")

	'''
	Here we are unzipping the bundles on remote machines.  
	'''

	os.system("""ssh -i """+SSH_KEY_PATH+""" """+USERNAME+"""@""" + vp_ip + """ \
		  "screen -m -d bash -c 'echo "Get ready! Crawler is about to start!";\
		  rm -rf """+ vp_bundle_name[:-4]+""";\
		  unzip """+ vp_bundle_name+""";'" """)


def start_crawler_on_all_machines(vp_ip,vp_bundle_name,SSH_KEY_PATH,USERNAME,vp_name):
	# copy the folder
	
   
	print "Starting process of resolving domain through BIND server for VP whose name is ", vp_name

	'''
	Here we are unzipping the bundles on remote machine before starting run.sh. Please note we first
	delete pre existing bundle data with rm -rf command. This is to ensure that when script starts
	we always have the data which is obtained by running script. without rm -rf, its possible that
	script gets struck and we end up thinking that old data was collected by the script we ran. 
	'''

	os.system("""ssh -i """+SSH_KEY_PATH+""" """+USERNAME+"""@""" + vp_ip + """ \
		  "screen -m -d bash -c 'echo "Get ready! Crawler is about to start!";\
		  cd ~/"""+ vp_bundle_name[:-4]+"""/DNS_pipeline_step_1/;\
		  bash ronaldo1.sh;'" """)

def get_active_domain_set(vp_ip,vp_bundle_name,SSH_KEY_PATH,USERNAME,vp_name):
	   
	print "Getting active set for VP whose name is ", vp_name

	os.system("scp -i " + SSH_KEY_PATH + " " + USERNAME+"@"\
		+ vp_ip + ":~/"+vp_bundle_name[:-4]+"/DNS_pipeline_step_1/step1_resolve_here/resolved_domains.txt ./active_domains_of_each_VP/")

	os.system("cat ./active_domains_of_each_VP/resolved_domains.txt > ./active_domains_of_each_VP/"+vp_name+"_active_set")


def return_active_domain_set(vp_ip,vp_bundle_name,SSH_KEY_PATH,USERNAME,vp_name):
	   
	print "Transfering active set back to VP whose name is ",vp_name

	os.system("scp -i " + SSH_KEY_PATH + " -r ./active_domains_of_each_VP/active_set.txt " + USERNAME+"@"\
		+ vp_ip + ":~/"+vp_bundle_name[:-4]+"/DNS_pipeline_step_1/step1_resolve_here/")



def start_DNS_traceroute_spoofing_check(vp_ip,vp_bundle_name,SSH_KEY_PATH,USERNAME,vp_name):
	print "Starting DNS traceroute and spoofing check for VP whose name is is ", vp_name

	'''
	Here we are unzipping the bundles on remote machine before starting run.sh. Please note we first
	delete pre existing bundle data with rm -rf command. This is to ensure that when script starts
	we always have the data which is obtained by running script. without rm -rf, its possible that
	script gets struck and we end up thinking that old data was collected by the script we ran. 
	'''

	os.system("""ssh -i """+SSH_KEY_PATH+""" """+USERNAME+"""@""" + vp_ip + """ \
		  "screen -m -d bash -c 'echo "Get ready! Crawler is about to start!";\
		  cd ~/"""+ vp_bundle_name[:-4]+"""/DNS_pipeline_step_1/;\
		  bash ronaldo2.sh;'" """)


def get_server_side_blocked(vp_ip,vp_bundle_name,SSH_KEY_PATH,USERNAME,vp_name):
	   
	print "Getting server side blocked domains for VP whose VP name is ", vp_name

	os.system("scp -i " + SSH_KEY_PATH + " " + USERNAME+"@"\
		+ vp_ip + ":~/"+vp_bundle_name[:-4]+"/DNS_pipeline_step_1/have_auth_no_ip_extended.common_three_runs.txt ./server_side_blocked_of_each_VP/")
	# This command can be used to find common lines based on 3rd column of file and print lines of second file
	#awk 'NR==FNR{a[$3,$3];next} ($3,$3) in a' test1 test2

	os.system("cat ./server_side_blocked_of_each_VP/have_auth_no_ip_extended.common_three_runs.txt > ./server_side_blocked_of_each_VP/"+vp_name+"_have_auth_no_ip_extended.common_three_runs.txt")



def return_server_side_blocked(vp_ip,vp_bundle_name,SSH_KEY_PATH,USERNAME,vp_name):
	   
	print "Returning server side blocked domains for VP whose VP name is ", vp_name

	os.system("scp -i " + SSH_KEY_PATH + " -r ./server_side_blocked_of_each_VP/have_auth_no_ip_extended.common_three_runs.txt " + USERNAME+"@"\
		+ vp_ip + ":~/"+vp_bundle_name[:-4]+"/DNS_pipeline_step_4/")


def start_MDA_DNS(vp_ip,vp_bundle_name,SSH_KEY_PATH,USERNAME,vp_name):
	print "Starting MDA DNS for VP whose name is ", vp_name

	
	os.system("""ssh -i """+SSH_KEY_PATH+""" """+USERNAME+"""@""" + vp_ip + """ \
		  "screen -m -d bash -c 'echo "Get ready! Crawler is about to start!";\
		  cd ~/"""+ vp_bundle_name[:-4]+"""/DNS_pipeline_step_4/;\
		  bash proximity.sh;'" """)

def start_path_stitching(vp_ip,vp_bundle_name,SSH_KEY_PATH,USERNAME,vp_name):
	print "Starting path stitching for VP whose name is is ", vp_name

	os.system("""ssh -i """+SSH_KEY_PATH+""" """+USERNAME+"""@""" + vp_ip + """ \
		  "screen -m -d bash -c 'echo "Get ready! Crawler is about to start!";\
		  cd ~/"""+ vp_bundle_name[:-4]+"""/DNS_pipeline_step_4/;\
		  bash data.sh;'" """)


def zip_and_get_back_collected_data(vp_ip,vp_bundle_name,SSH_KEY_PATH,USERNAME,vp_name):
	print "Starting compression and data transfer back to local machine for VP whose name is is ", vp_name

	os.system("""ssh -i """+SSH_KEY_PATH+""" """+USERNAME+"""@""" + vp_ip + """ \
		  "echo "Get ready! Crawler is about to start!";\
		  cd ~/"""+ vp_bundle_name[:-4]+"""/;\
		  zip -r DNS_data_of_"""+vp_name+""".zip ./DNS_pipeline_step_1 ./DNS_pipeline_step_2/step4_traceroute ./DNS_pipeline_step_2/fake_spoof_capture.pcap ./DNS_pipeline_step_3/actual_spoof_capture.pcap ./DNS_pipeline_step_4/MDA_DNS_scamper_output_temp.txt ./DNS_pipeline_step_3/spoof_capture.pcap ./DNS_pipeline_step_4/process_parser/complete_stitched_paths ./DNS_pipeline_step_4/progress_logs.txt;" """)

	os.system("scp -i " + SSH_KEY_PATH + " -r " + USERNAME+"@"\
		+ vp_ip + ":~/"+vp_bundle_name[:-4]+"/DNS_data_of_"+vp_name+".zip ./DNS_data_of_all_VPs/")

def start_get_summary(vp_ip,vp_bundle_name,SSH_KEY_PATH,USERNAME,vp_name):
	print "Getting summary for VP whose name is is ", vp_name
	# name odf resolved file resolved_domains.txt
	column_names=vp_name+",Resolved domains,Unresolved domains, Blocked domains, DNS traceroutes colpleted,MDA DNS traceroute completed"
	start=time.time()
	os.system("""ssh -i """+SSH_KEY_PATH+""" """+USERNAME+"""@""" + vp_ip + """ \
		  "screen -m -d bash -c 'cd ~/"""+ vp_bundle_name[:-4]+"""/;\
		  rm -rf stats;\
		  echo """+vp_name+""" >> stats;\
		  cat ./DNS_pipeline_step_1/step1_resolve_here/resolved_domains.txt | wc -l >> stats;\
		  cat ./DNS_pipeline_step_1/step1_resolve_here/blocked_domains.txt | wc -l >> stats;\
		  cat ./DNS_pipeline_step_1/have_auth_no_ip_extended.common_three_runs.txt | wc -l >> stats;\
		  ls ./DNS_pipeline_step_2/step4_traceroute/ | grep dnst | wc -l >> stats;\
		  cd DNS_pipeline_step_4/;\
		  bash remove_null_chr.sh;\
		  cd ..;\
		  cat ./DNS_pipeline_step_4/MDA_DNS_scamper_output_temp.txt | grep nodes | wc -l >> stats ;\
		  cat ./DNS_pipeline_step_4/process_parser/complete_stitched_paths/final_log | grep nodes | wc -l >> stats;\
          dig +retry=5 +short myip.opendns.com @resolver1.opendns.com >> stats;\
		  tcpdump -r ./DNS_pipeline_step_2/fake_spoof_capture.pcap | wc -l >> stats;\
		  tcpdump -r ./DNS_pipeline_step_3/actual_spoof_capture.pcap | wc -l >> stats;'" """)
	#This time is for dig to get public ip of remote machine
	time.sleep(1)
#	print "Time taken ",start-time.time()
	os.system("scp -i " + SSH_KEY_PATH + " " + USERNAME+"@"\
		+ vp_ip + ":~/"+vp_bundle_name[:-4]+"/stats ./summary/")

	os.system(" cat ./summary/stats | xargs | sed -e \'s/ /,/g\' > ./summary/"+vp_name+"_stats.txt")




if __name__ == "__main__":
	directories_to_store_data=["active_domains_of_each_VP","DNS_data_of_all_VPs","server_side_blocked_of_each_VP","summary"]
	for one_dir in directories_to_store_data:
		if not one_dir in os.listdir("."):
			os.system("mkdir "+one_dir)
	#start_vpn()
	#sys.exit()
#	time.sleep(100)
	# we wait for 100 seconds after starting VPN because once we start VPN command,  VPN starts working after 30 seconds or so
	with open("vantages",'r') as vantages:
		vantage_array=vantages.read().split("\n")

	skip_for_NordVPN_VPs=["SA","Australia","UK","Germany","Japan","China","US","Turkey"]
	skip_for_Cloud_VPs=["SA","Australia","Germany","China"]#["SA","UK","US","Australia","Russia","Turkey","Germany","Japan","China","PK"]#["SA"]#["SA","UK","US","Australia","Russia","Turkey","Germany","Japan","China","PK"]
	MODE=int(sys.argv[1])
	'''
	Mode 3, 5 and 9 get data from all VPs and store them in relevant directories. So, we need to clean directories with rm -rf command
	before we get the data for current run. This is to ensure we do not end up using data collected from old run 
	'''
	if MODE==1:
		print "************************** Warning **************************"
		print "The mode you chose deletes old data with rm -rf. if you don't\n\
			   intend to delete old data, please kill the process with CTRL+C"
		print "**************************************************************"
		time.sleep(5)
	elif MODE==3:
		os.system("rm -rf ./active_domains_of_each_VP/**")
	elif MODE==5:
		os.system("rm -rf ./server_side_blocked_of_each_VP/**")
	elif MODE==8:
		os.system("rm -rf ./DNS_data_of_all_VPs/**")
	elif MODE==9:
		os.system("rm -rf ./summary/**")
	elif MODE==10:
		start_vpn()
        
    
	for one_vp in vantage_array:
		if one_vp!="":
			one_vp_array=one_vp.split(",")
			vp_ip=one_vp_array[-1:][0]
			vp_name="_".join(one_vp_array)
			vp_country=one_vp_array[1]
			vp_bundle_name="DNS_BUNDLE.zip"
			'''
			As we use one key to SSH into EC2 machines and the other to SSH into One provider machines, we made two separate functions
			to start scripts in EC2 and One provider machines.
			'''

			if vp_name.find("NordVPN")>(-1):
				if vp_country in skip_for_NordVPN_VPs:
				#	print "Skipping running commands for ",vp_name
					continue
				if MODE==1:
					transfer_bundle_to_all_machines(vp_ip,vp_bundle_name,"~/.ssh/2b-proxy.pem","ubuntu",vp_name)
				elif MODE==2:
					start_crawler_on_all_machines(vp_ip,vp_bundle_name,"~/.ssh/2b-proxy.pem","ubuntu",vp_name)
				elif MODE==3:
					get_active_domain_set(vp_ip,vp_bundle_name,"~/.ssh/2b-proxy.pem","ubuntu",vp_name)
				elif MODE==4:
					start_DNS_traceroute_spoofing_check(vp_ip,vp_bundle_name,"~/.ssh/2b-proxy.pem","ubuntu",vp_name)
				elif MODE==5:					
					get_server_side_blocked(vp_ip,vp_bundle_name,"~/.ssh/2b-proxy.pem","ubuntu",vp_name)
				elif MODE==6:
					start_MDA_DNS(vp_ip,vp_bundle_name,"~/.ssh/2b-proxy.pem","ubuntu",vp_name)
				elif MODE==7:
					start_path_stitching(vp_ip,vp_bundle_name,"~/.ssh/2b-proxy.pem","ubuntu",vp_name)
				elif MODE==8:
					zip_and_get_back_collected_data(vp_ip,vp_bundle_name,"~/.ssh/2b-proxy.pem","ubuntu",vp_name)
				elif MODE==9:
					start_get_summary(vp_ip,vp_bundle_name,"~/.ssh/2b-proxy.pem","ubuntu",vp_name)



			if vp_name.find("Cloud")>(-1) or vp_name.find("Insitutional")>(-1):
				if vp_country in skip_for_Cloud_VPs:
				#	print "Skipping running commands for ",vp_name
					continue
				if MODE==1:
			 		transfer_bundle_to_all_machines(vp_ip,vp_bundle_name,"~/.ssh/stardust-lums","root",vp_name)
				elif MODE==2:
					start_crawler_on_all_machines(vp_ip,vp_bundle_name,"~/.ssh/stardust-lums","root",vp_name)
				elif MODE==3:
					get_active_domain_set(vp_ip,vp_bundle_name,"~/.ssh/stardust-lums","root",vp_name)
				elif MODE==4:
					start_DNS_traceroute_spoofing_check(vp_ip,vp_bundle_name,"~/.ssh/stardust-lums","root",vp_name)
				elif MODE==5:
					get_server_side_blocked(vp_ip,vp_bundle_name,"~/.ssh/stardust-lums","root",vp_name)
				elif MODE==6:
					start_MDA_DNS(vp_ip,vp_bundle_name,"~/.ssh/stardust-lums","root",vp_name)
				elif MODE==7:
					start_path_stitching(vp_ip,vp_bundle_name,"~/.ssh/stardust-lums","root",vp_name)
				elif MODE==8:
					zip_and_get_back_collected_data(vp_ip,vp_bundle_name,"~/.ssh/stardust-lums","root",vp_name)
				elif MODE==9:
					start_get_summary(vp_ip,vp_bundle_name,"~/.ssh/stardust-lums","root",vp_name)


	'''
	Please note below commands are meant to concatenate data collected from all VPs into one VP
		i) find command list downs all relevant files
		ii) xargs command concatenate files into one file with one '\n' between data of each file
		iii) sort command only keep unique lines
		iv) awk command removes extra spaces
	'''

	if MODE==3:
		os.system("find ./active_domains_of_each_VP/*_active_set* | xargs -I{} sh -c \"cat {}; echo \'\'\" | sort -u -k1,1 | awk \' {if($1!=\"\")print} \'> ./active_domains_of_each_VP/active_set.txt")
	elif MODE==5:
		os.system("find ./server_side_blocked_of_each_VP/*_have_auth* | xargs -I{} sh -c \"cat {}; echo \'\'\"   | sort -u -k2,2 | awk \' {if($1!=\"\")print} \'> ./server_side_blocked_of_each_VP/have_auth_no_ip_extended.common_three_runs.txt" )
	elif MODE==9:
		os.system("rm -rf ./summary/stats.csv")
		os.system("echo \"VP name,Resolved domains,Unresolved domains, Blocked domains,DNS traceroutes done ,MDA DNS done, Path stitched, Public IP of machine,Fake spoofed packets, Actual spoofed packets \" >> ./summary/stats.csv")
		os.system("find ./summary/*_stats* | xargs -I{} sh -c \"cat {}; echo \'\'\" | sort -u -k1,1 | awk \' {if($1!=\"\")print} \'>> ./summary/stats.csv")
		os.system("rm -rf ./summary/*.txt*")

	for one_vp in vantage_array:
		if one_vp!="":
			one_vp_array=one_vp.split(",")
			vp_ip=one_vp_array[-1:][0]
			vp_name="_".join(one_vp_array)
			vp_country=one_vp_array[1]
			vp_bundle_name="DNS_BUNDLE.zip"

			if vp_name.find("NordVPN")>(-1):
				if vp_country in skip_for_NordVPN_VPs:
				#	print "Skipping running commands for ",vp_name
					continue
				if MODE==3:
					return_active_domain_set(vp_ip,vp_bundle_name,"~/.ssh/2b-proxy.pem","ubuntu",vp_name)
				elif MODE==5:
					return_server_side_blocked(vp_ip,vp_bundle_name,"~/.ssh/2b-proxy.pem","ubuntu",vp_name)
			if vp_name.find("Cloud")>(-1) or vp_name.find("Insitutional")>(-1):
				if vp_country in skip_for_Cloud_VPs:
				#	print "Skipping running commands for ",vp_name
					continue
				if MODE==3:
					return_active_domain_set(vp_ip,vp_bundle_name,"~/.ssh/stardust-lums","root",vp_name)
				elif MODE==5:
					return_server_side_blocked(vp_ip,vp_bundle_name,"~/.ssh/stardust-lums","root",vp_name)
