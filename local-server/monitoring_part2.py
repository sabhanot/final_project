import sys
import scp
import netmiko
from netmiko import ConnectHandler
import json
global final_ds
import threading
from os.path import exists
import paramiko
from scp import SCPClient

def collect_log(ssh_conn):
    all_logs = ssh_conn.send_command("show log")
    return all_logs.split("\n")


def collect_cpu(ssh_conn):
    cpu_detail = ssh_conn.send_command("show process cpu sorted")
    cpu = cpu_detail.split("\n")[0]
    if cpu == "":
        cpu = cpu_detail.split("\n")[1]
    return [cpu_detail],[cpu]


def device_collection(ssh_conn,site,host):

    log_list = collect_log(ssh_conn)
    cpu_detail,cpu = collect_cpu(ssh_conn)
    # device_ds = {host:{"log":[],"CPU":cpu,"CPU_details":cpu_detail}}
    final_ds[site][host] = {"log":log_list,"CPU":cpu,"CPU_details":cpu_detail}
    print(f"{host} done")
def final_output(collected_otp,stored_otp):
    if stored_otp == None:
        return collected_otp

    for k,val in collected_otp["site-1"].items():
        # print(k)
        # print(len(stored_otp["site-1"][k]["log"]))
        temp_list = stored_otp["site-1"][k]["log"]
        temp_list = set(temp_list)
        final_temp = []
        for i in val["log"]:
            if i != "":
                if i not in temp_list:
                    final_temp.append(i)
        for i in final_temp:
            stored_otp["site-1"][k]["log"].append(i)
        # stored_otp["site-1"][k]["log"] = set(temp_list)
        stored_otp["site-1"][k]["CPU"].append(val["CPU"][0])
        stored_otp["site-1"][k]["CPU_details"].append(val["CPU_details"][0])
    return stored_otp




if __name__ == "__main__":
    aws_ip = sys.argv[1]

    devices = {"core-r1": "192.168.187.193","core-r2": "192.168.187.194","dist-sw1": "192.168.187.199","dist-sw2": "192.168.187.197"}
    # {core-r1:{log:[],cpu:[]}
    site = "site-1"
    final_ds = {site:{}}
    threads = []
    for host,host_ip in devices.items():
        dev_conn = {'device_type': 'cisco_ios', 'ip': host_ip, 'username': "cisco", 'password': "cisco", 'verbose': False, 'secret' :"cisco" }
        ssh_conn = ConnectHandler(**dev_conn)
        my_thread = threading.Thread(target=device_collection, args=(ssh_conn, site, host))
        my_thread.start()
        threads.append(my_thread)
    for t in threads:
        t.join()
    if exists("outputs/monitor_logs.json"):
        with open("outputs/monitor_logs.json") as f:
            data = json.load(f)
    else:
        data = None
    final_otp = final_output(final_ds,data)
    with open("outputs/monitor_logs.json",'w') as f:
        json.dump(final_otp,f,indent=4)
    print("LOGS COLLECTED FROM ALL THE DEVICES")
    print(f"Connecting to AWS-server {host_ip}")
    print("pushing the logs to AWS-server")
    client_1 = paramiko.SSHClient()
    client_1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client_1.connect(hostname=aws_ip, username="root", password="Final_project")
    scp = SCPClient(client_1.get_transport())
    scp.put("outputs/monitor_logs.json", "/etc/ansible/final_project/AWS-server")
