#!/bin/bash

echo 'Configuring IP-table rules..'

sudo iptables -D OUTPUT -p tcp --tcp-flags ALL RST,RST -j DROP
sudo iptables -D OUTPUT -p tcp --tcp-flags ALL RST,ACK -j DROP

sudo iptables -A OUTPUT -p tcp --tcp-flags ALL RST,RST -j DROP
sudo iptables -A OUTPUT -p tcp --tcp-flags ALL RST,ACK -j DROP

echo -e '\n'

echo 'Starting Scamper Measurements from US...'

cd ./../../

echo Total nonHTTP-Traceroutes to complete: $(wc -l < custom-files/US/nonhttp_cmd_file.txt) | tee -a custom-files/US/log.txt
echo 'Running scamper...'
sudo ./scamper -o custom-files/US/100k-US-nonhttp.txt -O text -O cmdfile -f custom-files/US/nonhttp_cmd_file.txt
wait
echo Total nonHTTP-Traceroutes completed: $(cat custom-files/US/100k-US-nonhttp.txt | grep -c trace) | tee -a custom-files/US/log.txt

echo -e '\n'

echo Total HTTP-Traceroutes to complete: $(wc -l < custom-files/US/http_cmd_file.txt) | tee -a custom-files/US/log.txt
echo 'Running scamper...'
sudo ./scamper -o custom-files/US/100k-US-http.txt -O text -O cmdfile -f custom-files/US/http_cmd_file.txt
wait
echo Total HTTP-Traceroutes completed: $(cat custom-files/US/100k-US-http.txt | grep -c trace) | tee -a custom-files/US/log.txt

echo -e '\nUS Measurement Complete!'
