#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
import requests
import argparse
import logging 
import logging.handlers

handler = logging.handlers.RotatingFileHandler("mylog.log");
formater = logging.Formatter("%(asctime)s -  %(name)s - %(filename)s:%(lineno)d - %(message)s")
handler.setFormatter(formater)

logger = logging.getLogger('main')
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def get_servers(url):
    """
    {
      "cluster_name": "B4183328234480d", 
      "ip": [
        {
          "addr": "34.161.230.12", 
          "type": "fixed"
        }, 
        {
          "addr": "172.17.1.37", 
          "type": "floating"
        }
      ], 
      "name": "Mysql-xDQNvbIZ-B4183328234480d", 
      "software_code": "database_server", 
      "status": "ACTIVE", 
      "uuid": "20eb4ca2-0af1-46f0-a9e5-0facd6ab1336"
    }
    """
    result = requests.get(url)
    return json.loads(result.text)['data']
    
def get_fixed_ip(ip_set):
    """
    ip_set is like: 
    [
        {
          "addr": "34.161.230.12", 
          "type": "fixed"
        }, 
        {
          "addr": "172.17.1.37", 
          "type": "floating"
        }
      ]
    """
    return [ip['addr'] for ip in ip_set if ip['type'] == 'fixed']
def get_floating_ip(ip_set):
    return [ip['addr'] for ip in ip_set if ip['type'] == 'floating']
    
def collect_windows_servers():
    url = "http://172.17.0.241:8080/api/v1.0/backend/user_list_servers/"
	
    data = get_servers(url)
    #print data
    renders = [da for da in data if da['name'][:6] == 'Render']
    webs = [da for da in data if da['name'][:5]=="HMWeb"]
    cluster = {}
    for web in webs:
        cluster[web['cluster_name']] = {'master_ip':ip['addr'] for ip in web['ip'] if ip['type'] == 'floating' }
        cluster[web['cluster_name']]['renders'] = []
        for server in renders:
            if web['cluster_name'] == server['cluster_name']:
                cluster[web['cluster_name']]['renders'].append(server)   
    #print json.dumps(cluster,indent=4)
    return cluster


def check_consul_status(ip):
    result = requests.get("http://"+ip+':8500/v1/catalog/nodes')
    #print json.dumps(result.text,indent=4)
    #result.text is string type
    return  json.loads(result.text)
    
def create_windows_inventory():
    """
    {
    "Node": "hmdata-vooijlml-b4190386310101d.novalocal", 
    "Datacenter": "dc1", 
    "Meta": {}, 
    "Address": "40.172.96.20", 
    "TaggedAddresses": {
        "wan": "40.172.96.20", 
        "lan": "40.172.96.20"
    }, 
    "ID": "72d8ad11-3597-4b76-7f83-efdb5aeec451", 
    "CreateIndex": 92787, 
    "ModifyIndex": 92803
    }

    """
    hosts={
        "renders": {
                "hosts": [],
                "vars": {
                        "ansible_ssh_user": "Administrator",
                        "ansible_ssh_pass": "win10@hermes",
                        "ansible_ssh_port":  5986 ,
                        "ansible_connection": "winrm",
                        "ansible_winrm_server_cert_validation":"ignore"
                }
        }
    }

    clusters = collect_windows_servers()

    for cluster_name,cluster in clusters.items():
        logger.debug( "cluster: %s" % json.dumps(cluster,indent=4))
        consul_nodes = [node['Address'] for node in check_consul_status(cluster['master_ip'])]
        logger.debug( "consul_nodes: %s" % consul_nodes )
        for render in cluster['renders']:
            if get_fixed_ip(render['ip'])[0]  in consul_nodes: #just for test.
                logger.debug( "consul on %s is running " % get_floating_ip(render['ip'])[0]) 
            else:
                logger.debug( "consul on %s is not running " % get_floating_ip(render['ip'])[0])
       
                hosts['renders']['hosts'].append(get_floating_ip(render['ip'])[0])
    
    logger.debug(json.dumps(hosts,indent=4))                
    return hosts

def get_hosts():
    hosts = create_windows_inventory()
    print json.dumps(hosts,indent=4)
def get_vars():
    hosts = create_windows_inventory()
    print json.dumps(hosts[host]['vars'])

if __name__ == "__main__":
    #check_consul_status("172.17.1.37")
    create_windows_inventory()
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--list',action='store_true',dest='list',help='get all hosts')
    parser.add_argument('--host',action='store',dest='host',help='get all hosts')
    args = parser.parse_args()

    if args.list:
        get_hosts()

    if args.host:
     
        get_vars(args.host)

