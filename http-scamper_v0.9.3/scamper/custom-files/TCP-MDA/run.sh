cp ./../../../../dns-scamper/scamper/scamper .

rm -rf invalid-ips.txt scamper_command.txt MDA_TCP_OUTPUT.txt
sleep 5
python run-mda-webservers.py resolved.txt



sudo ./scamper -o MDA_TCP_OUTPUT.txt -O cmdfile -f scamper_command.txt
