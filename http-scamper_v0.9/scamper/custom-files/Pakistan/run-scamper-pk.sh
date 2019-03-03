#!/bin/bash

echo 'Configuring IP-table rules..'

sudo iptables -D OUTPUT -p tcp --tcp-flags ALL RST,RST -j DROP
sudo iptables -D OUTPUT -p tcp --tcp-flags ALL RST,ACK -j DROP

sudo iptables -A OUTPUT -p tcp --tcp-flags ALL RST,RST -j DROP
sudo iptables -A OUTPUT -p tcp --tcp-flags ALL RST,ACK -j DROP

echo -e '\n'

echo 'Starting Scamper Measurements from Pakistan...'

cd ./../../

echo Total nonHTTP-Traceroutes to complete: $(wc -l < custom-files/Pakistan/nonhttp_cmd_file.txt) | tee -a custom-files/Pakistan/log.txt
echo 'Running scamper...'
sudo ./scamper -o custom-files/Pakistan/100k-Pakistan-nonhttp.txt -O text -O cmdfile -f custom-files/Pakistan/nonhttp_cmd_file.txt
wait
echo Total nonHTTP-Traceroutes completed: $(cat custom-files/Pakistan/100k-Pakistan-nonhttp.txt | grep -c trace) | tee -a custom-files/Pakistan/log.txt

echo -e '\n'

echo Total HTTP-Traceroutes to complete: $(wc -l < custom-files/Pakistan/http_cmd_file.txt) | tee -a custom-files/Pakistan/log.txt
echo 'Running scamper...'
sudo ./scamper -o custom-files/Pakistan/100k-Pakistan-http.txt -O text -O cmdfile -f custom-files/Pakistan/http_cmd_file.txt
wait
echo Total HTTP-Traceroutes completed: $(cat custom-files/Pakistan/100k-Pakistan-http.txt | grep -c trace) | tee -a custom-files/Pakistan/log.txt

echo -e '\nPakistan Measurement Complete!'
