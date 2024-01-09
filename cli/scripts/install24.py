
#  Copyright 2022-2024 PGEDGE  All rights reserved. #


import sys, os

VER = "24.1.6"
REPO = os.getenv("REPO", "https://pgedge-upstream.s3.amazonaws.com/REPO")

from urllib import request as urllib2

import tarfile, platform


def download_n_unpack(p_file, p_url, p_download_msg, p_del_download):
    if os.path.exists(p_file):
        os.system("rm -f " + p_file)

    print("Downloading " + str(p_download_msg))
    f = str(p_url) + "/" + p_file
    try:
        fu = urllib2.urlopen(f)
        local_file = open(p_file, "wb")
        local_file.write(fu.read())
        local_file.close()
    except Exception as e:
        print("ERROR: Unable to download " + f + "\n" + str(e))
        sys.exit(1)

    print("Unpacking ...")
    try:
        # Use 'data' filter if available, but revert to Python 3.11 behavior ('fully_trusted') 
        #   if this feature is not available:
        tar = tarfile.open(p_file)
        tar.extraction_filter = getattr(tarfile, 'data_filter',
                                       (lambda member, path: member))
        tar.extractall()
        tar.close()
        if p_del_download == True:
            os.remove(p_file)
    except Exception as e:
        print("ERROR: Unable to unpack \n" + str(e))
        sys.exit(1)


# MAINLINE ##################################

IS_64BITS = sys.maxsize > 2**32
if not IS_64BITS:
    print("ERROR: This is a 32-bit machine and our packages are 64-bit.")
    sys.exit(1)

if os.path.exists("pgedge"):
    dir = os.listdir("pgedge")
    if len(dir) != 0:
        print("ERROR: Cannot install over a non-empty 'pgedge' directory.")
        sys.exit(1)

my_file = "pgedge-ctl-" + VER + ".tar.bz2"
download_n_unpack(my_file, REPO, "CLI " + VER + " ...", True)

cmd = "pgedge" + os.sep + "ctl "
os.system(cmd + "set GLOBAL REPO " + REPO)
os.system(cmd + "update --silent")
os.system(cmd + "info")
os.system(cmd + "install ctlibs")

print("\npgedge/ctl installed.\n")

sys.exit(0)
