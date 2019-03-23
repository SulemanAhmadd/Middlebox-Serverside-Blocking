#!/bin/bash

echo '> Configuring IP-table rules...'

sudo iptables -A OUTPUT -p tcp --tcp-flags ALL RST,RST -j DROP
sudo iptables -A OUTPUT -p tcp --tcp-flags ALL RST,ACK -j DROP

echo '> Starting Scamper Measurements from Russia...'

cd ./../../

echo Total nonHTTP-Traceroutes to complete: $(wc -l < custom-files/Russia/nonhttp_cmd_file.txt) | tee -a custom-files/Russia/log.txt
echo '> Running scamper...'
sudo ./scamper -o custom-files/Russia/nonhttp-results.txt -O text -O cmdfile -f custom-files/Russia/nonhttp_cmd_file.txt
wait
(echo Total nonHTTP-Traceroutes completed: $(cat custom-files/Russia/nonhttp-results.txt | grep -c trace)) | tee -a custom-files/Russia/log.txt

echo -e '\n'

echo Total HTTP-Traceroutes to complete: $(wc -l < custom-files/Russia/http_cmd_file.txt) | tee -a custom-files/Russia/log.txt
echo '> Running scamper...'
sudo ./scamper -o custom-files/Russia/http-results.txt -O text -O cmdfile -f custom-files/Russia/http_cmd_file.txt
wait
echo Total HTTP-Traceroutes completed: $(cat custom-files/Russia/http-results.txt | grep -c trace) | tee -a custom-files/Russia/log.txt

echo -e '\n> Russia Measurement Complete!'

sudo iptables -D OUTPUT -p tcp --tcp-flags ALL RST,RST -j DROP
sudo iptables -D OUTPUT -p tcp --tcp-flags ALL RST,ACK -j DROP

echo '> IP-table rules removed'
