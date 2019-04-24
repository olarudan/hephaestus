from hephaestus.config import config
from hephaestus.ssh import SSH
from hephaestus.modules.apt import Apt
from hephaestus.modules.service import Service
from hephaestus.modules.file import File

import os
import sys
import logging
import yaml

class TaskRunner:
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
    try:

      for host in self.hosts:
        # create ssh connection
        ssh_client = SSH(host)
        ssh_client.connect()

        for task in self.tasks:
          module = list(task)[1]
          print ("TASK(%s module - [ %s ]): %s" %((module), host, task['name']))

          # apt module
          if (module == 'apt'):
            apt_task = Apt(task, ssh_client)
            self.msg(apt_task.execute_action())

          # file module
          elif (module == 'file'):
            file_task = File(task, ssh_client)
            self.msg(file_task.execute_action())

          # service
          elif (module == 'service'):
            service_task = Service(task, ssh_client)
            self.msg(service_task.execute_action())
    except:
      pass
    finally:
      ssh_client.close()
