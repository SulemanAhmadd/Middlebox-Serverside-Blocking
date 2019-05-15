#!/bin/bash

cd ./../../

sudo ./scamper -o custom-files/Test-DNS/$1 -O text -O cmdfile -f custom-files/Test-DNS/$2
wait