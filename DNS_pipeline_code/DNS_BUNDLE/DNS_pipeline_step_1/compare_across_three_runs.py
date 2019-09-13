import os

BASE_DIR = os.getcwd() #/Users/mjav/tmp_test"
runs = ["run1", "run2", "run3"]

no_auth_cmd='''cat blocked_domain_ns_info.txt | awk '{if($1!=""&& $1!="root"&& $1!="The" && $4=="")print$1" "$(NF)}' >no_auth_no_ip_extended.txt'''

auth_cmd='''cat blocked_domain_ns_info.txt | awk '{if($4!=""&& $1!="root" && $1!="The")print$1" "$6" "$(NF)}' > have_auth_no_ip_extended.txt'''


def prep_data():
    for run in runs: 
        os.system("pwd")   
        os.chdir(os.path.join(BASE_DIR, run))

        # prep data
        os.system(no_auth_cmd)
        os.system(auth_cmd)


def compare_across_runs():
    os.chdir(BASE_DIR)
    no_auth_no_ip = dict()
    have_auth_no_ip = dict()
     
    for run in runs:
        no_auth_no_ip[run] = set()
        have_auth_no_ip[run] = set()

        with open(os.path.join(BASE_DIR, run, "no_auth_no_ip_extended.txt")) as f:
            no_auth_no_ip[run] = set([line.strip() for line in f.readlines()])

        with open(os.path.join(BASE_DIR, run, "have_auth_no_ip_extended.txt")) as f:
            have_auth_no_ip[run] = set([line.strip() for line in f.readlines()])


    no_auth_no_ip_common = reduce(lambda x,y: x&y, no_auth_no_ip.values())
    have_auth_no_ip_common = reduce(lambda x,y: x&y, have_auth_no_ip.values())

    with open("no_auth_no_ip_extended.common_three_runs.txt", "w") as wf:
        wf.write("\n".join(no_auth_no_ip_common))

    with open("have_auth_no_ip_extended.common_three_runs.txt", "w") as wf:
        wf.write("\n".join(have_auth_no_ip_common))

    with open("blocked_stats.txt", "w") as wf:
        wf.write("\n".join(["No auth: " + str(len(no_auth_no_ip_common)),
                            "Have auth: " + str(len(have_auth_no_ip_common))]))


if __name__ == "__main__":
    prep_data()
    compare_across_runs()
