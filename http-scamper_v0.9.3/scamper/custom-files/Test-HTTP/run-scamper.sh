#!/bin/bash

cd ./../../

sudo ./scamper -o custom-files/Test-HTTP/$4 -O text -O cmdfile -f custom-files/Test-HTTP/$2
wait

sudo ./scamper -o custom-files/Test-HTTP/$3 -O text -O cmdfile -f custom-files/Test-HTTP/$1
wait
