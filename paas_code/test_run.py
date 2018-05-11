from ansible_api import MyRunner
import json
#ansible = MyRunner('/etc/ansible/hosts')


ansible = MyRunner('./get_server.py')
ansible.run('renders', 'win_shell', "paasInit")
#ansible.run('all', 'setup', "filter='ansible_mounts'")
result=ansible.get_result()
succ = result['success']

failed = result['failed']
unreachable = result['unreachable']
for key,value in succ.iteritems():
    print key
    print json.dumps(value,indent=4)
