import sys

try:
    os.remove('proximity_test_passed_and_reverse_test_passed')
except:
    pass

try:
    all_prox = []
    with open("proximity_test_passed", 'r') as prox_pass:
        for line in prox_pass:
            line = line.strip()
            line_eles = line.split('\t')
            dom = line_eles[0]
            all_prox.append(dom)

    all_spoof = []
    with open("received_spoofed_response", 'r') as recv_spf:
        for line in recv_spf:
            line = line.strip()
            dom = line[:-1]
            all_spoof.append(dom)

    for each_prox in all_prox:
        if each_prox in all_spoof:
            with open("proximity_test_passed_and_reverse_test_passed", 'a') as intrsc:
                intrsc.write(each_prox + '\n')

except Exception as err:
    print("Error in both_pass.py - " + str(err))
    sys.exit(1)
