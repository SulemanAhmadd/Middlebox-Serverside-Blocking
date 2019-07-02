
#####################**Testing** #####################  

For Testing (a sample of 100 IPs):  
Go to directory - *cd http-scamper_v0.9/scamper/custom-files/Test-Run*  
Make script executable - *chmod +x run-scamper-test.sh*  
Then execute the shell script - *./run-scamper-test.sh*  

#####################**Project Measurements** #####################  

For **Pakistan** Machine:  
Go to directory - *cd http-scamper_v0.9/scamper/custom-files/Pakistan*  
Make script executable - *chmod +x run-scamper-pk.sh*  
Then execute the shell script - *./run-scamper-pk.sh*  

For **Russia** Machine:  
Go to directory - *cd http-scamper_v0.9/scamper/custom-files/Russia*  
Make script executable -  *chmod +x run-scamper-ru.sh*  
Then execute the shell script - *./run-scamper-ru.sh*  

For **US** Machine:  
Go to directory - *cd http-scamper_v0.9/scamper/custom-files/US*  
Make script executable -  *chmod +x run-scamper-us.sh*  
Then execute the shell script - *./run-scamper-us.sh*  

##################### **General Usage** #####################

- **Installation:**
Once inside the *http-scamper* directory, open terminal and write:

./configure

Once configuration completes, then type:

sudo make

( If an error during make, please run *autoreconf -f -i* )

- **Pre-Requisites:**
Before using the tool please setup IP table rules:  

sudo iptables -A OUTPUT -p tcp --tcp-flags ALL RST,RST -j DROP  
sudo iptables -A OUTPUT -p tcp --tcp-flags ALL RST,ACK -j DROP

- **Usage:**
For the purpose of this project only the following commands are important:
  - Run scamper on a list of commands:  
      ./scamper -o [output-path] -O text -O cmdfile -f [input-command-file-path]
      
  - Run scamper for a single IP address:
      - TCP:  
           ./scamper 'trace -P TCP -s [source-port] -d 80 [IPv4-Address]'
      - ICMP:  
           ./scamper 'trace -P ICMP-paris [IPv4-Address]'
      - UDP:  
           ./scamper 'trace -P UDP-paris -d 53 [IPv4-Address]'
      - HTTP:  
           ./scamper 'trace -P TCP -s [source-port] -d 80 -H [domain-name] [IPv4-Address]'
      - HTTP-Save HTML:  
           ./scamper 'trace -P TCP -s [source-port] -d 80 -F -H [domain-name] [IPv4-Address]'
           
           (For this mode make sure the directory 'custom-files/http_payload' already exists)
