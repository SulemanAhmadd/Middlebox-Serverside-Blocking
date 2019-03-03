#!/bin/bash

echo 'Configuring IP-table rules..'

sudo iptables -D OUTPUT -p tcp --tcp-flags ALL RST,RST -j DROP
sudo iptables -D OUTPUT -p tcp --tcp-flags ALL RST,ACK -j DROP

sudo iptables -A OUTPUT -p tcp --tcp-flags ALL RST,RST -j DROP
sudo iptables -A OUTPUT -p tcp --tcp-flags ALL RST,ACK -j DROP

echo -e '\n'

echo 'Starting Scamper Measurements ...'

cd ./../../

echo Total nonHTTP-Traceroutes to complete: $(wc -l < custom-files/Test-Run/nonhttp_cmd_file.txt) | tee -a custom-files/Test-Run/log.txt
echo 'Running scamper...'
sudo ./scamper -o custom-files/Test-Run/100k-Test-Run-nonhttp.txt -O text -O cmdfile -f custom-files/Test-Run/nonhttp_cmd_file.txt
wait
echo Total nonHTTP-Traceroutes completed: $(cat custom-files/Test-Run/100k-Test-Run-nonhttp.txt | grep -c trace) | tee -a custom-files/Test-Run/log.txt

echo -e '\n'

echo Total HTTP-Traceroutes to complete: $(wc -l < custom-files/Test-Run/http_cmd_file.txt) | tee -a custom-files/Test-Run/log.txt
echo 'Running scamper...'
sudo ./scamper -o custom-files/Test-Run/100k-Test-Run-http.txt -O text -O cmdfile -f custom-files/Test-Run/http_cmd_file.txt
wait
echo Total HTTP-Traceroutes completed: $(cat custom-files/Test-Run/100k-Test-Run-http.txt | grep -c trace) | tee -a custom-files/Test-Run/log.txt

echo -e '\nTest-Run Measurement Complete!'
