from hephaestus.config import config
import logging
import sys

class Service:
  """
  A class used to abstract the management of System V init scripts (services)

  This class handles the restarting of a service. It is designed to be idempotent.

  Attributes
  ----------
  task : dict
      name - name of the task
      action - action of the task (restart)
      service - the action is going to be perfomred on a service
  ssh_client: obj
      the ssh client used to execute the ssh commands on the remote host

  Methods
  -------
  is_installed()
      checks weather a package is installed (used to guarantee idempotency)
  execute_action()
      installs or removes an apt package on a remote host
  """

  def __init__(self, task, ssh_client):
    self.log = logging.getLogger(__name__)

    # get module name from module __name__
    module = __name__.split('.')[-1]

    # make sure valid actions are selected `restart`
    if (task[module]['action'] in ['restart']):
      self.action = task[module]['action']
    else:
      msg = "Invalid actions were provided for % module, please correct them. Valid options are: `restart`" % (__name__)
      self.log.error(msg)
      raise Exception(msg)

    self.name = task['name']
    self.ssh_client = ssh_client
    self.service = task[module]['name']
    

  def is_installed(self):
    """ Checks weather an apt package is installed on a remote host.

    This method crafts a command based on `dpck-query` to figure out if an apt package is istalled.

    Returns
    ------
    bool:
        True if package is installed
        False if package is not installed
    """
    # use this function to guarantee indempotence
    cmd = "dpkg-query -W -f='${Status}' %s 2>/dev/null | grep -c \"ok installed\"" % (self.service)
    stdout, stderr = self.ssh_client.execute(cmd)

    # a return value of 1 means the package is present, 0 means its absent
    if (stdout[0].rstrip() == '1'):
      return True
    else:
      return False

  def is_running(self):
    """ Checks weather a service is running.

    This method crafts a command based on `service` program to figure out is running.

    Returns
    ------
    bool:
        True if service is running
        False if service is not running
    """
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
    """ Restarts a service on a remote host

    This method crafts a command based on `service` program to install or remove an apt package.

    Returns
    ------
    bool:
        True if package was removed
        False if no action was taken (i.e. package was already installed)
    """
    if (self.is_installed()): # install package
      cmd = "service %s %s" % (self.service, self.action)
      stdout, stderr = self.ssh_client.execute(cmd)
      if (self.is_running):
        return True
      else:
        self.log.error("Failed to %s `%s`. Please debug manually." % (self.action, self.service))
        sys.exit(1)
        
    else:
      msg = "Failed to %s `%s` because the service does not exist." % (self.action, self.service)
      self.log.error(msg)
      #raise Exception(msg)
      return False
