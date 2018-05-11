# -*- coding:utf-8 -*-
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from tempfile import NamedTemporaryFile
from ansible.plugins.callback import CallbackBase
import os

class MyRunner(object):  
    """ 
    This is a General object for parallel execute modules. 
    """  
    def __init__(self, resource, *args, **kwargs):  
        self.resource = resource  
        self.inventory = None  
        self.variable_manager = None  
        self.loader = None  
        self.options = None  
        self.passwords = None  
        self.callback = None  
        self.__initializeData()  
        self.results_raw = {}  
  
    def __initializeData(self):  
        """ 
        初始化ansible 
        """
       
        Options = namedtuple('Options',
                             ['connection', 'module_path', 'forks', 'become', 'become_method', 'become_user', 'check',
                              'diff'])
 
        self.loader = DataLoader()
  
        self.options = Options(connection='winrm', module_path='/path/to/mymodules', forks=100, become=None,
                               become_method=None, become_user=None, check=False,
                               diff=False)
     
        self.passwords = dict(vault_pass='secret')
        self.inventory = InventoryManager(loader=self.loader, sources=self.resource)
        self.variable_manager = VariableManager(loader=self.loader, inventory=self.inventory)
      
  
    def run(self, host_list, module_name, module_args,):  
        """ 
        run module from andible ad-hoc. 
        module_name: ansible module_name 
        module_args: ansible module args 
        """  
        # create play with tasks  
        play_source = dict(  
                name="Ansible Play",  
                hosts=host_list,  
                gather_facts='no',  
                tasks=[dict(action=dict(module=module_name, args=module_args))]  
        )  
        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)  
  
        # actually run it  
        tqm = None  
        self.callback = ResultsCollector()  
        try:  
            tqm = TaskQueueManager(  
                    inventory=self.inventory,  
                    variable_manager=self.variable_manager,  
                    loader=self.loader,  
                    options=self.options,  
                    passwords=self.passwords,
                    stdout_callback='default', 
            )  
            tqm._stdout_callback = self.callback  
            result = tqm.run(play)  
        finally:  
            if tqm is not None:  
                tqm.cleanup()  
  
  
    def get_result(self):  
        self.results_raw = {'success':{}, 'failed':{}, 'unreachable':{}}  
        for host, result in self.callback.host_ok.items():  
            self.results_raw['success'][host] = result._result  
  
        for host, result in self.callback.host_failed.items():  
            self.results_raw['failed'][host] = result._result
  
        for host, result in self.callback.host_unreachable.items():  
            self.results_raw['unreachable'][host]= result._result['msg']  
  
        #print "Ansible执行结果集:%s"%self.results_raw
        return self.results_raw

class ResultsCollector(CallbackBase):  
  
    def __init__(self, *args, **kwargs):  
        super(ResultsCollector, self).__init__(*args, **kwargs)  
        self.host_ok = {}  
        self.host_unreachable = {}  
        self.host_failed = {}  
  
    def v2_runner_on_unreachable(self, result):  
        self.host_unreachable[result._host.get_name()] = result  
  
    def v2_runner_on_ok(self, result,  *args, **kwargs):  
        self.host_ok[result._host.get_name()] = result  
  
    def v2_runner_on_failed(self, result,  *args, **kwargs):  
        self.host_failed[result._host.get_name()] = result
