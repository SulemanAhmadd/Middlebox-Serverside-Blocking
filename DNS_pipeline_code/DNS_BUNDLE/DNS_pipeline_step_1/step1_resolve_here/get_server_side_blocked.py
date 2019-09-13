with open("blocked_domains.txt",'r') as blocked:
	blocked_domains=blocked.read().split("\n")[:-1]
with open("active_set.txt",'r') as active:
	active_domains=active.read().split("\n")[:-1]
for one_blocked_domain in blocked_domains:
	for one_active_domain in active_domains:
		active_domain=one_active_domain.split(" ")[0]
		if one_blocked_domain!="" and one_blocked_domain==active_domain:
			with open("../step3_resolve_again_get_ns/server_side_blocked.txt",'a') as ssb:
				ssb.write(one_blocked_domain+"\n")
