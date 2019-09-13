sudo apt-get update -y
sudo apt-get install bind9 bind9utils bind9-doc -y
cd /etc/bind
echo "acl goodclients {
    192.0.2.0/24;
    localhost;
    localnets;
};

options {
	directory \"/var/cache/bind\";
	recursion yes;
    	allow-query { goodclients; };
	// If there is a firewall between you and nameservers you want
	// to talk to, you may need to fix the firewall to allow multiple
	// ports to talk.  See http://www.kb.cert.org/vuls/id/800113

	// If your ISP provided one or more IP addresses for stable 
	// nameservers, you probably want to use them as forwarders.  
	// Uncomment the following block, and insert the addresses replacing 
	// the all-0's placeholder.

	// forwarders {
	// 	0.0.0.0;
	// };
	dnssec-validation no;
	//========================================================================
	// If BIND logs error messages about the root key being expired,
	// you will need to update your keys.  See https://www.isc.org/bind-keys
	//========================================================================
//	dnssec-validation auto;
	auth-nxdomain no;    # conform to RFC1035
//	listen-on-v6 { any; };
};" > named.conf.options

echo "// This is the primary configuration file for the BIND DNS server named.
//
// Please read /usr/share/doc/bind9/README.Debian.gz for information on the 
// structure of BIND configuration files in Debian, *BEFORE* you customize 
// this configuration file.
//
// If you are just adding zones, please do that in /etc/bind/named.conf.local

include \"/etc/bind/named.conf.options\";
include \"/etc/bind/named.conf.local\";
include \"/etc/bind/named.conf.default-zones\";

server ::/0 {
       edns no;

};

server 0.0.0.0/0 {
       edns no;

};" > named.conf
echo "# run resolvconf?
RESOLVCONF=no

# startup options for the server
OPTIONS=\"-4 -u bind\"" > /etc/default/bind9
named-checkconf
service bind9 restart