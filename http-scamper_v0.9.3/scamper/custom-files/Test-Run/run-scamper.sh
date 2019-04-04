#!/bin/bash

cd ./../../

sudo ./scamper -o custom-files/Test-Run/$4 -O text -O cmdfile -f custom-files/Test-Run/$2
wait

sudo ./scamper -o custom-files/Test-Run/$3 -O text -O cmdfile -f custom-files/Test-Run/$1
wait
