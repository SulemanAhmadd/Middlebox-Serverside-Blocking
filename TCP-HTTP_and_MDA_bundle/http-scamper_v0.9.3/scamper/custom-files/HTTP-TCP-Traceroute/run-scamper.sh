#!/bin/bash

cd ./../../

sudo ./scamper -o custom-files/HTTP-TCP-Traceroute/$4 -O text -O cmdfile -f custom-files/HTTP-TCP-Traceroute/$2
wait

sudo ./scamper -o custom-files/HTTP-TCP-Traceroute/$3 -O text -O cmdfile -f custom-files/HTTP-TCP-Traceroute/$1
wait
