We can collect data for DNS pipeline in 3 steps which are listed below

- Run **bash run1.sh** to distribute bundle to VPs and start DNS resolution of input list with BIND server.

Now wait until first bash script is executing.

- After **run1.sh** has collected data, run the command **bash run2.sh** to start DNS traceroutes and spoofing check on domains available in one of the control country but unavilable in test country.

Now, again wait until **run2.sh** is executing.

- Finall, run the **bash run3.sh** to do MDA DNS on master input list
