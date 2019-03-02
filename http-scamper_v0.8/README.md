-**Installation:**
Once inside the http scamper directory, open terminal and write:

./configure

Onece configuration completes, then type:

sudo make

(If an error during make, please run *autoreconf -f -i*)

-**Pre-Requisites:**
Before using the tool please setup IP table rules:

sudo iptables -A OUTPUT -p tcp --tcp-flags ALL RST,RST -j DROP
sudo iptables -A OUTPUT -p tcp --tcp-flags ALL RST,ACK -j DROP

-**Usage:**
For the purpose of this project only the following commands are important:
  - Run scamper on a list of commands:
      ./scamper -o [output-path] -O text -O cmdfile -f [input-command-path]
      
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
