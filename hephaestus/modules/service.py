from hephaestus.config import config
import logging
import sys

class Service:
  def __init__(self, task, ssh_client):
    self.log = logging.getLogger(__name__)

    # make sure valid actions are selected `restart`
    if (task['module']['action'] in ['restart']):
      self.action = task['module']['action']
    else:
      msg = "Invalid actions were provided for % module, please correct them. Valid options are: `restart`" % (__name__)
      self.log.error(msg)
      raise Exception(msg)

    self.name = task['name']
    self.ssh_client = ssh_client
    self.service = task['module']['service']
    

  def is_installed(self):
    # use this function to guarantee indempotence
    cmd = "dpkg-query -W -f='${Status}' %s 2>/dev/null | grep -c \"ok installed\"" % (self.service)
    stdout, stderr = self.ssh_client.execute(cmd)

    # a return value of 1 means the package is present, 0 means its absent
    if (stdout[0].rstrip() == '1'):
      return True
    else:
      return False

  def is_running(self):
    # use this function to guarantee indempotence
    cmd = "service %s status" % (self.service)

    if (self.is_installed()):
      stdout, stderr = self.ssh_client.execute(cmd)
    else: # don't even bother if service is not installed
      return False

    # a return value of 1 means the package is present, 0 means its absent
    if ("%s is running" %(self.service) in ''.join(stdout)):
      return True
    else:
      return False


  def execute_action(self):
    if (self.is_installed()): # install package
      cmd = "service %s %s" % (self.service, self.action)
      stdout, stderr = self.ssh_client.execute(cmd)
      if (self.is_running):
        return True
      else:
        self.log.error("Failed to %s `%s`. Please debug manually." % (self.action, self.service))
        sys.exit(1)
        
    else:
      self.log.error("Failed to %s `%s` because the service does not exist." % (self.action, self.service))
      sys.exit(1)
