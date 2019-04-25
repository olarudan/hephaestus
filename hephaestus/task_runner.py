from hephaestus.config import config
from hephaestus.ssh import SSH
import importlib

import os
import sys
import logging
import yaml

class TaskRunner:
  """
  A class used to run tasks on a remote hosts.

  This class is responsible for running a list of tasks encapsulated in a manifest file. It will also figure out
  the module (`apt`, `service`, `file`) responsible for executing a particular task.The tasks runner can run 
  a manifest against multiple hosts by iterating over the hosts file that contains one hostname per line.

  Attributes
  ----------
  tasks : dict
      tasks to be executed loaded from a manifest YAML file.
  hosts : list
      list of hostnames that the manifest will be applied on 

  Methods
  -------
  mgs()
      helper method to display the status of the task execution
  run()
      executes tasks from a manifest file on hostnames from the hosts file.
  """

  def __init__(self):
    # load manifest file
    with open(config['manifest']) as yml_file:
      self.tasks = yaml.load(yml_file)

    # load hosts file
    with open(config['hosts']) as f:
      self.hosts = [x.strip() for x in f.readlines()]

  def msg(self, task):
    if task:
      print "SUCCESS\n"
    else:
      print "NO CHANGE\n"

  def run(self):
    """ Executes tasks from a manifest file on hostnames from the hosts file.

    This method will iterate over each host in the hosts file and execute a list of tasks from a manifest file.
    Each task is going to be assigned a module responsible for the executing it. It will also make sure to close
    the ssh connection after running all tasks for a particular host. The progress of the task runner will be
    output to the screen in the following format: TASK( {{ module_name }} - [ {{ hostname }} ]): {{ task_name }}
    """

    try:
      for host in self.hosts:
        # create ssh connection
        ssh_client = SSH(host)
        ssh_client.connect()

        for task in self.tasks:
          module = list(task)[1]
          print ("TASK(%s module - [ %s ]): %s" %((module), host, task['name']))

          # load module and instantiate class objects dynamically
          # the following convention should be followed: Class name is capitalized.
          hep_module = importlib.import_module("hephaestus.modules.%s" % (module))
          hep_class = getattr(hep_module, module.capitalize())
          hep_task = hep_class(task, ssh_client)
          self.msg(hep_task.execute_action())

      # close ssh connection
      ssh_client.close()
    except:
      pass
      # log an error here
    finally:
      # close ssh connection
      ssh_client.close()
