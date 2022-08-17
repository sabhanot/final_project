import netmiko
from netmiko import ConnectHandler
from netaddr import *
import json
import ipaddress
import threading
import yaml
global subnet
# breaking the given subnet into two, first part will be used for interfaces and next half reserved for other uses
global interface_subnet
# breaking interface_subnet into /30 subnets to assign it to interfaces
global all_interface_subnets
global int_address_mapping
global switch_vlan
global all_switch_subnet
global final_DS

def get_hostname(ssh_conn):
    hostname = ssh_conn.send_command("show run | in hostname")
    return hostname.split()[1]

def get_cdp_neighbor(ssh_conn,interface):
    if interface == "Ethernet0/0":
        return None,None,None
    # print(interface)
    int_id = interface[-3:]
    # print(int_id)
    cdp_output = ssh_conn.send_command("show cdp ne")
    # print(cdp_output)
    for j in cdp_output.split("\n"):
        spli_j = j.split()
        if len(spli_j) > 3:
            if spli_j[2] == int_id:
                return spli_j[0].split(".")[0],spli_j[-1],spli_j[2]
    return None,None,None

def get_description(cdp_string):
    lst = ["to",cdp_string]
    return "-".join(lst)

def get_ospfAreaId(cdp_neighbor,site):
    if cdp_neighbor.split("-")[0] == "core":
        return "0"
    else:
        return site.split("-")[1]

def get_nextAvailableIP_subnet():
    next_ip = all_interface_subnets[0]
    all_interface_subnets.remove(next_ip)
    return next_ip

def addIP(lst):
    # print(lst)
    res_lst = []
    spli_lst = lst.split(".")
    for index,i in enumerate(spli_lst):
        if index == len(spli_lst)-1:
            last_octet = int(i)
            last_octet = last_octet + 1
            res_lst.append(str(last_octet))
        else:
            res_lst.append(i)
    return ".".join(res_lst)


def get_nextIP(IP_list):
    if len(IP_list) == 1:
        subnet_nextip =  IP_list[0]
        spli_subnet = subnet_nextip.split("/")
        IP_nextIP = spli_subnet[0]
        # netmask = IPNetwork(IP_list[0]).netmask
    else:
        IP_nextIP = IP_list[1]
        # netmask = IPNetwork(IP_list[0]).netmask
    netmask = IPNetwork(IP_list[0]).netmask
    # spli_subnet = subnet.split("/")
    IP_add = addIP(IP_nextIP)
    # netmask = IPNetwork(abc).netmask
    lst = [IP_add,str(netmask)]
    return lst

def get_interfaces_info(ssh_conn,site):
    res_ds = []
    show_ip = ssh_conn.send_command("show ip int br")
    int_list = []
    each_int = {}
    for index,i in enumerate(show_ip.split("\n")):
        if index == 0:
            continue
        int_list.append(i.split()[0])
    # print(int_list)
    for i in int_list:
        # cmd_1 = f"interface {i}"
        # send_commands = [f"interface {i}","no sh"]
        # ssh_conn.send_config_set(send_commands)
        cdp_neighbor,remote_interface_id,local_interface_id = get_cdp_neighbor(ssh_conn,i)
        hostname = get_hostname(ssh_conn)
        # print(cdp_neighbor)
        if cdp_neighbor != None:
            unique_cdp = "_".join([hostname,local_interface_id])
            unique_cdp_neighbor = "_".join([cdp_neighbor,remote_interface_id])
            # print(unique_cdp)
            # print(unique_cdp_neighbor)
            if unique_cdp_neighbor in int_address_mapping:
                ip_address = get_nextIP(int_address_mapping[unique_cdp_neighbor])
            else:
                int_subnet = get_nextAvailableIP_subnet()
                # print(int_subnet)
                int_subnet = str(int_subnet)
                ip_address = get_nextIP([int_subnet])
                int_address_mapping[unique_cdp] = [int_subnet,ip_address[0]]
            # print(ip_address)
            description = get_description(cdp_neighbor)
            ospf_area_id = get_ospfAreaId(cdp_neighbor,site)
            each_int = {"interface_id":i,"description":description,"ospf_area_id":ospf_area_id,"address":ip_address[0],"netmask":ip_address[1]}
            # print(each_int)
            res_ds.append(each_int)
    return res_ds

def router_info(ssh_conn,site):
    hostname = get_hostname(ssh_conn)
    interface_list = get_interfaces_info(ssh_conn,site)
    result_ds = {"hostname": hostname,"interfaces":interface_list}
    final_DS["routers"].append(result_ds)
    print("router done")

# def get_switchIPaddress_subnet():
#     subnet_sw = all_switch_subnet.pop()
#     return subnet_sw
def get_nextIP_switch(vlan_id):
    ip_add = str(switch_vlan[vlan_id]["avail_ip"].pop())
    switch_vlan[vlan_id]["used_ip"].append(ip_add)
    netmask = str(IPNetwork(switch_vlan[vlan_id]["subnet"]).netmask)
    # print(type(netmask))
    return ip_add,netmask


def get_svi(site):
    site_no = site.split("-")[1]
    svi_interface_info= []
    for i in switch_vlan:
        svi_dict = {}
        # print(i)
        svi_dict["description"] = f"virtual interface for vlan {i}"
        svi_dict["interface_id"] = i
        add_svi,netmask_svi = get_nextIP_switch(i)
        svi_dict["address"] = add_svi
        svi_dict["netmask"] = netmask_svi
        svi_dict["ospf_area_id"] = site_no
        svi_interface_info.append(svi_dict)
        # print(svi_interface_info)
    return svi_interface_info

    # ip_subnet = get_switchIPaddress_subnet()
    # ip_address = get_nextIP_switch(ip_subnet)



def switch_info(ssh_conn,site,access_interface,vlans_list):
    # print("inside switch")
    hostname = get_hostname(ssh_conn)
    interface_list = get_interfaces_info(ssh_conn,site)
    for i in interface_list:
        i["ospf_area_id"] = "1"
    svi_int_list = get_svi(site)
    # print(svi_int_list)
    # for i in svi_int_list:
    #     interface_list.append(i)
    access_int_list = []

    for k,val in access_interface[hostname].items():
        temp_dict = {}
        temp_dict["interface_id"] = k
        temp_dict["vlan_id"] = val
        access_int_list.append(temp_dict)

    result_ds = {"hostname": hostname,"interfaces":interface_list,"access_interfaces":access_int_list,"SVI_interfaces":svi_int_list}
    print("switch done")
    final_DS["switches"].append(result_ds)

def device_info(ssh,site,access_interface,vlans_list):
    # all_info = {"site":site,"switches":[],"routers":[]}

    hostname = get_hostname(ssh_conn)
    ospf_process_id = "1"
    which_device = hostname.split("-")[1][0]
    if which_device == "r":
        router_info(ssh_conn,site)
    elif which_device == "s":
        switch_info(ssh,site,access_interface,vlans_list)






if __name__ == "__main__":
    devices = {"core-r1": "192.168.187.193","core-r2": "192.168.187.194","dist-sw1": "192.168.187.199","dist-sw2": "192.168.187.197"}
    subnet = "192.168.1.0/24"
    # # breaking the given subnet into two, first part will be used for interfaces and next half reserved for other uses
    interface_subnet = list(IPNetwork(subnet).subnet(25))[0]
    switch_vlan_subnet = list(IPNetwork(subnet).subnet(25))[1]

    switch_vlan_list = ["vlan 10","vlan 20","vlan 30","vlan 40"]
    switch_vlan = {}
    all_switch_subnet = list(IPNetwork(switch_vlan_subnet).subnet(28))
    access_interface = {"dist-sw1":{"Ethernet1/0":"vlan 10","Ethernet1/1":"vlan 20"},"dist-sw2":{"Ethernet2/0":"vlan 20","Ethernet2/1":"vlan 10","Ethernet2/2":"vlan 30"}}
    # # breaking interface_subnet into /30 subnets to assign it to interfaces
    all_interface_subnets = list(IPNetwork(interface_subnet).subnet(30))
    for i in range(len(switch_vlan_list)):
        subnet = str(all_switch_subnet.pop())
        ip_address_list = list(ipaddress.IPv4Network(str(subnet)))
        del ip_address_list[0]
        del ip_address_list[-1]
        switch_vlan[switch_vlan_list[i]] = {"subnet":subnet,"used_ip":[],"avail_ip":ip_address_list}
    int_address_mapping = {}
    site = "site-1"
    final_DS = {"site":site,"routers":[],"switches":[]}
    threads = []
    for name,ip in devices.items():
        dev_conn = {'device_type': 'cisco_ios', 'ip': ip, 'username': "cisco", 'password': "cisco", 'verbose': False, 'secret' :"cisco" }
        ssh_conn = ConnectHandler(**dev_conn)
        my_thread = threading.Thread(target=device_info, args=(ssh_conn, site, access_interface,switch_vlan_list))
        my_thread.start()
        threads.append(my_thread)
        # dev_ice,info_dict = device_info(ssh_conn,site,access_interface)
        # final_DS[dev_ice].append(info_dict)
    for t in threads:
        t.join()
    # for some_thread in threading.enumerate():
    #     print(some_thread)
    #     if some_thread != main_thread:
    #         some_thread.join()

    # print(final_DS)
    with open("outputs/all_logs_site.json","w") as f:
        json.dump(final_DS,f,indent=4)
    with open("outputs/all_logs_site.yml","w") as f:
        yaml.dump(final_DS,f)
    print('"all_logs_site.yml" yaml file created')


