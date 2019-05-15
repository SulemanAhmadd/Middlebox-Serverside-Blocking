#!/bin/bash

cd ./../../

sudo ./scamper -o custom-files/TCP-MDA/$2 -O text -O cmdfile -f custom-files/TCP-MDA/$1
wait
