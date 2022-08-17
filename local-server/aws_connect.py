import os
import sys

import paramiko
import scp
from scp import SCPClient
import netmiko
from netmiko import *
import threading
import time
def apply_config(ssh_conn,host):
    print(f"Applying config to {host}")
    with open(f"{host}.txt") as f:
        r = f.readlines()
    ouput = ssh_conn.send_config_set(r)
    print(ouput)
# client = paramiko.SSHClient()
host_ip = sys.argv[1]
print(f"Connecting to AWS-server {host_ip}")
client_1 = paramiko.SSHClient()
client_1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client_1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client_1.connect(hostname=host_ip, username="root", password="Final_project")
scp = SCPClient(client_1.get_transport())
scp.put("outputs/all_logs_site.yml", "/etc/ansible/final_project/ztp/roles/router/vars/main.yml")
scp.put("outputs/all_logs_site.yml", "/etc/ansible/final_project/ztp/roles/switch/vars/main.yml")
print("Pushed the yaml file obtained from info_collection to AWS in /etc/ansible/final_project/ztp/roles/router/vars/main.yml")
print("Pushed the yaml file obtained from info_collection to AWS in /etc/ansible/final_project/ztp/roles/switch/vars/main.yml")
print("Running ansible playbook to create configuration")

# print(scp.put("all_logs_site.yml", "/etc/ansible/final_project/ztp/roles/switch/vars/"))
stdin,stdout,stderr = client_1.exec_command("ansible-playbook /etc/ansible/final_project/ztp/site.yml")
# time.sleep(10)
print(stdout.read().decode("ascii"))
intput,output,error = client_1.exec_command("ls /etc/ansible/final_project/ztp/CONFIGS")
# print(output.read().decode("ascii"))
print("Below files created")
for i in output.read().decode("ascii").split("\n"):
    if i == "":
        continue
    print(i)
    path = f"/etc/ansible/final_project/ztp/CONFIGS/{i}"
    scp.get(path)
print("Retriving the config files from the AWS server")
devices = {"core-r1": "192.168.187.193","core-r2": "192.168.187.194","dist-sw1": "192.168.187.199","dist-sw2": "192.168.187.197"}
threads = []
for name,ip in devices.items():
    dev_conn = {'device_type': 'cisco_ios', 'ip': ip, 'username': "cisco", 'password': "cisco", 'verbose': False, 'secret' :"cisco" }
    ssh_conn = ConnectHandler(**dev_conn)
    # apply_config(ssh_conn,name)
    my_thread = threading.Thread(target=apply_config, args=(ssh_conn, name))
    my_thread.start()
    threads.append(my_thread)
for t in threads:
    t.join()
