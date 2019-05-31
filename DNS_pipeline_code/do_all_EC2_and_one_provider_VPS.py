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
				"Australia": "18.236.74.55",
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
		 if VP in ["Turkey", "Australia"]:
			continue

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
		if VP in ["Turkey"]:
			continue

		print "Starting VPN for", VP

		# First kill any existing vpn process
		os.system("""ssh -i ~/.ssh/2b-proxy.pem ubuntu@""" + VP_IP_map[VP] + """ "bash -c 'sudo pkill -f openvpn;'" """)

		os.system("""ssh -i ~/.ssh/2b-proxy.pem ubuntu@""" + VP_IP_map[VP] + """ "screen -m -d bash -c 'cd ~/NordVPN/; bash start_vpn.sh;'" """)


def transfer_bundle_to_all_machines(vp_ip,vp_bundle_name,SSH_KEY_PATH,USERNAME,vp_name):
   
	print "Starting data transfer for VP whose name is ", vp_name

	# Here we are transfering bundle to relevant EC2 machines
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
	
   
	print "Starting process of resolving domain through BIND server for VP whose  name is ", vp_name

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
	print "Starting DNS traceroute and spoofing chech for VP whose bundle name is ", vp_name

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

	os.system("cat ./server_side_blocked_of_each_VP/have_auth_no_ip_extended.common_three_runs.txt > ./server_side_blocked_of_each_VP/"+vp_name+"_have_auth_no_ip_extended.common_three_runs.txt")



def return_server_side_blocked(vp_ip,vp_bundle_name,SSH_KEY_PATH,USERNAME,vp_name):
	   
	print "Returning server side blocked domains for VP whose VP name is ", vp_name

	os.system("scp -i " + SSH_KEY_PATH + " -r ./server_side_blocked_of_each_VP/have_auth_no_ip_extended.common_three_runs.txt " + USERNAME+"@"\
		+ vp_ip + ":~/"+vp_bundle_name[:-4]+"/DNS_pipeline_step_4/")


def start_MDA_DNS(vp_ip,vp_bundle_name,SSH_KEY_PATH,USERNAME,vp_name):
	print "Starting MDA DNS for VP whose bundle name is ", vp_name

	
	os.system("""ssh -i """+SSH_KEY_PATH+""" """+USERNAME+"""@""" + vp_ip + """ \
		  "screen -m -d bash -c 'echo "Get ready! Crawler is about to start!";\
		  cd ~/"""+ vp_bundle_name[:-4]+"""/DNS_pipeline_step_4/;\
		  bash proximity.sh;'" """)

def start_path_stitching(vp_ip,vp_bundle_name,SSH_KEY_PATH,USERNAME,vp_name):
	print "Starting path stitching for VP whose bundle name is ", vp_name

	os.system("""ssh -i """+SSH_KEY_PATH+""" """+USERNAME+"""@""" + vp_ip + """ \
		  "screen -m -d bash -c 'echo "Get ready! Crawler is about to start!";\
		  cd ~/"""+ vp_bundle_name[:-4]+"""/DNS_pipeline_step_4/;\
		  bash data.sh;'" """)


def zip_and_get_back_collected_data(vp_ip,vp_bundle_name,SSH_KEY_PATH,USERNAME,vp_name):
	print "Starting compressioon and data transfer back to local machine for VP whose bundle name is ", vp_name

	os.system("""ssh -i """+SSH_KEY_PATH+""" """+USERNAME+"""@""" + vp_ip + """ \
		  "echo "Get ready! Crawler is about to start!";\
		  cd ~/"""+ vp_bundle_name[:-4]+"""/;\
		  zip -r DNS_data_of_"""+vp_name+""".zip ./DNS_pipeline_step_2/step4_traceroute ./DNS_pipeline_step_2/spoof_capture.pcap ./DNS_pipeline_step_3/spoof_capture.pcap ./DNS_pipeline_step_4/process_parser/complete_stitched_paths;" """)

	os.system("scp -i " + SSH_KEY_PATH + " -r " + USERNAME+"@"\
		+ vp_ip + ":~/"+vp_bundle_name[:-4]+"/DNS_data_of_"+vp_name+".zip ./DNS_data_of_all_VPs/")

if __name__ == "__main__":
#	start_vpn()
#	time.sleep(100)
	# we wait for 100 seconds after starting VPN because once we start VPN command,  VPN starts working after 30 seconds or so
	with open("vantages",'r') as vantages:
		vantage_array=vantages.read().split("\n")

	skip_for_NordVPN_VPs=[]#["SA","Australia","UK","Germany","Japan","China"]
	skip_for_Cloud_VPs=[]#["US","Russia","Turkey","Germany","Japan","China","PK"]
	MODE=int(sys.argv[1])
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




	if MODE==3:
		os.system("find ./active_domains_of_each_VP/*_active_set* | xargs -I{} sh -c \"cat {}; echo \'\'\" | sort -u -k1,1 | awk \' {if($1!=\"\")print} \'> ./active_domains_of_each_VP/active_set.txt")
	elif MODE==5:
		os.system("find ./server_side_blocked_of_each_VP/*_have_auth* | xargs -I{} sh -c \"cat {}; echo \'\'\"   | sort -u -k2,2 | awk \' {if($1!=\"\")print} \'> ./server_side_blocked_of_each_VP/have_auth_no_ip_extended.common_three_runs.txt" )

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
