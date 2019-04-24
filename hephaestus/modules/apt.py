from hephaestus.config import config
import logging

class Apt:
  def __init__(self, task, ssh_client):
    self.log = logging.getLogger(__name__)

    # get module name from module __name__
    module = __name__.split('.')[-1]

    # make sure valid actions are selected `install` or `remove`
    if (task[module]['action'] in ['remove', 'install']):
      self.action = task[module]['action']
    else:
      msg = 'Invalid actions were provided for Apt module, please correct them. Valid options are: `install` and `remove`'
      self.log.error(msg)
      raise Exception(msg)

    self.name = task['name']
    self.ssh_client = ssh_client
    self.package = task[module]['package']
    
  def is_installed(self):
    # use this function to guarantee indempotence
    cmd = "dpkg-query -W -f='${Status}' %s 2>/dev/null | grep -c \"ok installed\"" % (self.package)
    stdout, stderr = self.ssh_client.execute(cmd)

    # a return value of 1 means the package is present, 0 means its absent
    if (stdout[0].rstrip() == '1'):
      return True
    else:
      return False

  def execute_action(self):
    is_package_installed = self.is_installed()

    if ((not is_package_installed) and (self.action == 'install')): # install package
      cmd = "echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections && apt-get update && apt-get %s %s -y" % (self.action, self.package)
      stdout, stderr = self.ssh_client.execute(cmd)
      return True

    elif ((is_package_installed) and (self.action == 'remove')): # remove package
      cmd = "apt-get %s %s -y" % (self.action, self.package)
      stdout, stderr = self.ssh_client.execute(cmd)
      return True

    else: # everything else assumes no change
      return False
