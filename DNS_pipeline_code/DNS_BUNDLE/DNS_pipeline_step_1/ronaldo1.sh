mkdir run1
mkdir run2
mkdir run3
echo 'finding server side blocked domains first before finding auth servers' >> progress_logs.txt
date >> progress_logs.txt
python3 ./step1_resolve_here/my_bind.py
cat step1_resolve_here/*fail* | awk '{print$1}' > step1_resolve_here/blocked_domains.txt
cat step1_resolve_here/*success* > step1_resolve_here/resolved_domains.txt
rm step1_resolve_here/*success*
rm step1_resolve_here/*fail*
date >> progress_logs.txt
echo 'first step completed. finding auth servers now 1st time' >> progress_logs.txt
