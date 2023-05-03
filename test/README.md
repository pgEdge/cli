
## /etc/ansible/inventory #################################

[build]
el9  ansible_host=172.31.45.16
arm9 ansible_host=172.31.2.45
arm8 ansible_host=172.31.38.180
el8  ansible_host=172.31.35.192

[build:vars]
ansible_ssh_user=rocky
ansible_ssh_private_key_file=/home/rocky/keys/oscg-partners-new-key.pem


## Sample Ansible Commands #################################
ansible build -m command -a "git -C \$NC pull"
ansible el9 -m command -a "\$NC/build_all.sh 16"

## Sample AC commands
./ac build "git -C $NC pull"
./ac el9   "$NC/build_all.sh 16"
./ac el8   "$BLD/build-all-pgbin.sh 16"
./ac build "$BLD/build-all-components.sh spock 16"


