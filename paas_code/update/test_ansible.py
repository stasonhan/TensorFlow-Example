#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import json
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
#from ansible.inventory import Inventory
from ansible.inventory.manager import InventoryManager as Inventory
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase

# Create a callback object so we can capture the output
class ResultCallback(CallbackBase):
    """A sample callback plugin used for performing an action as results come in

    If you want to collect all results into a single object for processing at
    the end of the execution, look into utilizing the ``json`` callback plugin
    or writing your own custom callback plugin
    """
    def v2_runner_on_ok(self, result, **kwargs):
        """Print a json representation of the result

        This method could store the result in an instance attribute for retrieval later
        """
        host = result._host
        print (json.dumps({host.name: result._result}, indent=4))


def ansibleRun(host_list,task_list):
    Options = namedtuple('Options',
                         ['connection','module_path','forks','remote_user','private_key_file',
                          'ssh_common_args','ssh_extra_args','sftp_extra_args','scp_extra_args',
                          'become','become_method','become_user','verbosity','check'])

    # initialize needed objects
    variable_manager = VariableManager()
    loader = DataLoader()
    options = Options(  connection='smart',module_path=None,
                        forks=100,remote_user=None,private_key_file=None,ssh_common_args=None,ssh_extra_args=None,
                        sftp_extra_args=None,scp_extra_args=None,become=None,become_method=None,
                        become_user=None,verbosity=None,check=False
                     )

    passwords = dict()


    # Instantiate our ResultCallback for handling results as they come in
    results_callback = ResultCallback()

    # create inventory and pass to var manager
    inventory = Inventory(loader=loader, variable_manager=variable_manager, host_list=host_list)
    variable_manager.set_inventory(inventory)

    # create play with tasks
    play_source =  dict(
            name = "Ansible Play",
            hosts = host_list,
            gather_facts = 'no',
            tasks = task_list
        )
    play = Play().load(play_source, variable_manager=variable_manager, loader=loader)

    # actually run it
    tqm = None
    try:
        tqm = TaskQueueManager(
                inventory=inventory,variable_manager=variable_manager,
                loader=loader,options=options,passwords=passwords,
                stdout_callback=results_callback,  # Use our custom callback instead of the ``default`` callback plugin
            )
        result = tqm.run(play)
    finally:
        if tqm is not None:
            tqm.cleanup()

if __name__ == '__main__':
    host_list = ['172.17.1.104', '172.17.1.94']
    tasks_list = [
        dict(action=dict(module='command', args='pwd')),
        # dict(action=dict(module='shell', args='python sleep.py')),
        # dict(action=dict(module='synchronize', args='src=/home/op/test dest=/home/op/ delete=yes')),
    ]
    ansibleRun(host_list,tasks_list)
