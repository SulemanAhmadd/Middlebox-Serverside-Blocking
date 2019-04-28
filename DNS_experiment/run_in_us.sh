pwd
echo 'old directory deleted!'
cd /root/pakistan
python3 get_ip.py
python spoof.py
cp /root/scamper .
echo "scamper about to start"
sudo ./scamper -o hello.txt -O cmdfile -f run.txt &
echo "scamper started"

