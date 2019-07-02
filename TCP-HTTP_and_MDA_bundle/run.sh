cat TCP_HTTP_traceroute_input.txt > ./http-scamper_v0.9.3/scamper/custom-files/HTTP-TCP-Traceroute/resolved.txt
cat TCP_MDA_input.txt > ./http-scamper_v0.9.3/scamper/custom-files/TCP-MDA/resolved.txt
cd ./http-scamper_v0.9.3/scamper/custom-files/HTTP-TCP-Traceroute
echo "I am in the following directory"
pwd
date
bash run.sh

echo 'First task done'
cd ..
cd TCP-MDA/
bash run.sh
date
