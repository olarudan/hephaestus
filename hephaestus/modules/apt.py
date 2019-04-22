from hephaestus.config import config
from hephaestus.ssh import ssh

class Apt:
  def __init__(self, task):
    try:
      self.package = task['module']['package']
      self.action = task['module']['action']
      self.name = task['name']
    except:
      pass
      # log error here
    
  def is_installed(self):
    # use this function to guarantee indempotence
    result = ssh.execut("dpkg -s %s" % (self.package))
    if (result == 0):
      return True
    else:
      return False

  def execute(self):
      if self.is_installed():
        ssh.execute("apt-get %s %s -y" % (self.action, self.package))
        #log the change here
      else:
        pass
        #log that nothing has been changed
