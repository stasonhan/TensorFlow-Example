#!/usr/bin/python
import json
import argparse
hosts={
        "renders": {
                "hosts": ["172.17.1.102","172.17.1.94"],
                "vars": {
                        "ansible_ssh_user": "Administrator",
                        "ansible_ssh_pass": "win10@hermes",
                        "ansible_ssh_port" :5986,
                        "ansible_connection":"winrm",
                        "ansible_winrm_server_cert_validation":"ignore" 
                }
        }
}

def getList():
    print json.dumps(hosts)
def getVars(host):
    print json.dumps(hosts[host]['vars'])
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--list',action='store_true',dest='list',help='get all hosts')
    parser.add_argument('--host',action='store',dest='host',help='get all hosts')
    args = parser.parse_args()
 
    if args.list:
        getList()
 
    if args.host:
        getVars(args.host)
