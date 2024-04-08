
## /etc/ansible/hosts #####################################

[build]
el9  ansible_host=172.31.45.16
arm9 ansible_host=172.31.15.65

[test]
#EL9
t9a  ansible_host=172.31.25.101
t9   ansible_host=172.31.26.42

#Ubuntu 22.04
t22a ansible_host=172.31.18.9
t22  ansible_host=172.31.17.199

[all:vars]
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


