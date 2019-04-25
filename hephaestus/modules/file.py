from hephaestus.config import config
import logging
import sys
import os

class File:
  """
  A class used to abstract the management of apt packages.

  This class will either remove or install an apt package on a debian distro. It is designed to be idempotent.

  Attributes
  ----------
  task : dict
      name - name of the task
      action - action of the task (present or absent)
      package - the action is going to be perfomred on an apt package
      src - path to the source file
      dest - path to the destination (remote host) file
      dest_tmp - temporary path to the destination file 
      owner - user on the remote machine
      group - group on the remote machine
      mod - mode in octal (i.e 777 read/write/execute for user/group/other)
  ssh_client: obj
      the ssh client used to execute the ssh commands on the remote host

  Methods
  -------
  file_exists()
      checks if a file exists on the remote host
  execute_action()
      creates or removes a file on the remote host
  get_file_mod()
      gets mod of the dest file
  set_file_mod()
      sets mod of the dest file
  get_file_owner()
      gets owner of the dest file
  set_file_owner()
      sets owner of the dest file
  get_file_group()
      gets group of the dest file
  set_file_group()
      sets group of the dest file
  remove_file(file_name)
      remove a file on the remote host
  compare_dest_files()
      compare dest file and dest_temp file to see if the files are identical (does not check owner/group/mod)
  """

  def __init__(self, task, ssh_client):
    self.log = logging.getLogger(__name__)

    # get module name from module __name__ 
    module = __name__.split('.')[-1]

    # make sure valid actions are selected `present` and `absent`
    if (task[module]['action'] in ['present', 'absent']):
      self.action = task[module]['action']
    else:
      msg = "Invalid actions were provided for % module, please correct them. Valid options are: `present` and `absent` " % (__name__)
      self.log.error(msg)
      raise Exception(msg)

    self.name = task['name']
    self.ssh_client = ssh_client
    self.src = task[module]['src']
    self.dest = task[module]['dest']
    self.dest_tmp = "/tmp/%s" % (os.path.basename(self.dest))
    self.owner = task[module]['owner']
    self.group = task[module]['group']
    self.mod = task[module]['mod']
    

  def file_exists(self):
    """ Checks weather the dest file exists

    This method crafts a command based on `os.path.isfile` python function to figure out if a file
    exists on the remote host. It will run the python function through the python cli.

    Returns
    ------
    bool:
        True if dest file exists
        False if dest file does not exist
    """

    # use this function to guarantee indempotence
    cmd = "python -c \"exec(\\\"import os\\nprint os.path.isfile('%s')\\\")\"" % (self.dest)
    stdout, stderr = self.ssh_client.execute(cmd)

    # a return value of 1 means the package is present, 0 means its absent
    if ('True' in stdout[0]):
      return True
    else:
      return False


  def get_file_mod(self):
    """ Gets file mod of the dest file

    This method crafts a command based on `os.stat` python function to figure the mod of the dest file.
    It will run the python function through the python cli.

    Returns
    ------
    int:
        mod of the dest file in oct base
    """

    cmd = "python -c \"exec(\\\"import os\\nprint oct(os.stat('%s').st_mode)[4:]\\\")\"" % (self.dest)
    stdout, stderr = self.ssh_client.execute(cmd)
    return int(stdout[0])


  def set_file_mod(self):
    """ Sets file mod of the dest file

    This method crafts a command based on `os.chmod` python function to set the mod of the dest file.
    It will run the python function through the python cli.
    """

    cmd = "python -c \"exec(\\\"import os\\nos.chmod('%s', 0%d)\\\")\"" % (self.dest, int(self.mod))
    stdout, stderr = self.ssh_client.execute(cmd)


  def get_file_owner(self):
    """ Gets file owner of the dest file

    This method crafts a command based on `pwd.getpwuid` python function to figure the owner of the dest file.
    It will run the python function through the python cli.

    Returns
    ------
    str:
        owner of the dest file
    """

    cmd = "python -c \"exec(\\\"import os,pwd\\nprint pwd.getpwuid(os.stat('%s').st_uid).pw_name\\\")\"" % (self.dest)
    stdout, stderr = self.ssh_client.execute(cmd)
    return stdout[0]


  def set_file_owner(self):
    """ Sets file owner of the dest file

    This method crafts a command based on `os.chown` python function to set the owner of the dest file.
    It will run the python function through the python cli.
    """

    cmd = "python -c \"exec(\\\"import os,pwd\\nos.chown('%s', pwd.getpwnam('%s').pw_uid, -1)\\\")\"" % (self.dest, self.owner)
    stdout, stderr = self.ssh_client.execute(cmd)


  def get_file_group(self):
    """ Gets file group of the dest file

    This method crafts a command based on `grp.getgrgid` python function to figure the owner of the dest file.
    It will run the python function through the python cli.

    Returns
    ------
    str:
        group of the dest file
    """

    cmd = "python -c \"exec(\\\"import os,grp\\nprint grp.getgrgid(os.stat('%s').st_gid).gr_name\\\")\"" % (self.dest)
    stdout, stderr = self.ssh_client.execute(cmd)
    return stdout[0]


  def set_file_group(self):
    """ Sets file group of the dest file

    This method crafts a command based on `os.chown` python function to set the group of the dest file.
    It will run the python function through the python cli.
    """

    cmd = "python -c \"exec(\\\"import os,grp\\nos.chown('%s', -1, grp.getgrnam('%s').gr_gid)\\\")\"" % (self.dest, self.group)
    stdout, stderr = self.ssh_client.execute(cmd)
  

  def remove_file(self, file_name):
    """ Removes a file on the remote host

    This method crafts a command based on `os.remove` python function to remove the file.
    It will run the python function through the python cli. It will check for the existance of the file
    before removing it in order to guarantee idempotency

    Parameters:
    ----------
    file_name : str
        path to the remote file that is to be removed

    Returns
    ------
    bool:
        True, if the file was removed
        False, if there was no change
    """

    if (self.file_exists()):
      cmd = "python -c \"exec(\\\"import os,grp\\nos.remove('%s')\\\")\"" % (file_name)
      stdout, stderr = self.ssh_client.execute(cmd)
      return True
    else:
      return False


  def compare_dest_files(self):
    """ Compares two files to figure out if they are identical

    This method crafts a command based on `filecmp.cmp` python function to ccompare the dest file with dest_tmp
    in order to guarantee idempotency. It doesn't ignored owner/group/mod of the files.

    Returns
    ------
    bool:
        True, if dest file and dest_tmp file are identical
        False, if dest file and dest_tmp file are NOT identical
    """

    cmd = "python -c \"exec(\\\"import filecmp\\nprint filecmp.cmp('%s', '%s')\\\")\"" % (self.dest, self.dest_tmp)
    stdout, stderr = self.ssh_client.execute(cmd)

    if ('True' in stdout[0]):
      return True
    else:
      return False
    

  def execute_action(self):
    """ Creates or removes a dest file.

    This method puts everything together. For the `present` action it will copy the src file to a /tmp folder,
    compare it with the dest file (if it exists), then check owner/group/mod of the dest file (if exists), finally
    it will replace the file only if dest file and dest_tmp files are truly identical (including owner/group/mod).
    All of this is done to guarantee idempotency. For the `absent` action the method will first check if the
    dest file is present before removing it (guaranteeing idempotency)

    Returns
    ------
    bool:
        True, if the action was executed successfully (preset/absent)
        False, if no changes ocurred
    """

    # present action
    if (self.action == 'present'):
      try:
        # copy src file to dest tmp folder
        self.ssh_client.copy_file(self.src, self.dest_tmp)
        if (self.file_exists()): # if dest file exists proceed futher, otherwise just copy the src file to dest, no need to do anything else
          if not (self.compare_dest_files()): # files are identical (insure idempotency)
            # mod, owner, group are identical (insure idempotency)
            if not ((self.get_file_mod == self.mod) and (self.get_file_owner == self.owner) and (self.get_file_group == self.group)):
              # copy src file to dest
              self.ssh_client.copy_file(self.src, self.dest)
              return True
            else:
              return False
          else:
            return False
        else:
          # copy src file to dest file because dest file does not exist
          self.ssh_client.copy_file(self.src, self.dest)
          return True
      except:
        self.log.error('Failed to execute module `%` with action `%s`') % (__name__, self.action) 
      finally:
        # remove tmp file
        self.remove_file(self.dest_tmp)
    # absent action
    elif (self.action == 'absent'):
      if (self.file_exists()): # (insure idempotency)
        self.remove_file(self.dest)
        return True
      else:
        return False
