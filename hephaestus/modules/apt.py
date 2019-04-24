from hephaestus.config import config
import logging

class Apt:
  """
  A class used to abstract the management of apt packages.

  This class will either remove or install an apt package on a debian distro. It is designed to be idempotent.

  Attributes
  ----------
  task : dict
      name - name of the task
      action - action of the task (remove or install)
      package - the action is going to be perfomred on an apt package
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
    """ Checks weather an apt package is installed on a remote host.

    This method crafts a command based on `dpck-query` to figure out if an apt package is istalled.

    Returns
    ------
    bool:
        True if package is installed
        False if package is not installed
    """

    # use this function to guarantee indempotence
    cmd = "dpkg-query -W -f='${Status}' %s 2>/dev/null | grep -c \"ok installed\"" % (self.package)
    stdout, stderr = self.ssh_client.execute(cmd)

    # a return value of 1 means the package is present, 0 means its absent
    if (stdout[0].rstrip() == '1'):
      return True
    else:
      return False

  def execute_action(self):
    """ Installs or removes an apt package on a remote host

    This method crafts a command based on `apt-get` to install or remove an apt package.

    Returns
    ------
    bool:
        True if package was removed
        False if no action was taken (i.e. package was already installed)
    """
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
