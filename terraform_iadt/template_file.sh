#!/bin/bash
yum update -y
yum -y install git
sed -i "/^[^#]*PasswordAuthentication[[:space:]]no/c\PasswordAuthentication yes" /etc/ssh/sshd_config
echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
git clone https://github.com/sabhanot/final_project.git
amazon-linux-extras install ansible2
echo "Final_project" | passwd --stdin root
systemctl restart sshd
echo -e "[local-host]\nlocalhost ansible_user=root ansible_ssh_pass=Final_project" > /etc/ansible/hosts
echo -e "[defaults]\ninventory      = /etc/ansible/hosts\nhost_key_checking = false" > /etc/ansible/ansible.cfg
cp -r final_project /etc/ansible
pip3 install xlsxwriter
