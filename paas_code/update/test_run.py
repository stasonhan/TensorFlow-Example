from ansible_api import MyRunner
#
#ansible = MyRunner('/etc/ansible/hosts')


ansible = MyRunner('./getHost.py')
#ansible.run('renders', 'copy', "src=./update.zip dest=/home/update")
ansible.run('renders', 'unarchive', "src=./update.zip dest=/home/update")
ansible.run('renders','shell',"systemctl restart network")
ansible.run('renders','shell',"echo 'hello ' > /home/update/update.log")
result=ansible.get_result()
succ = result['success']

failed = result['failed']
unreachable = result['unreachable']
for key,value in succ.iteritems():
    print key,value
