from hephaestus.config import config
import logging
import sys
import os

class File:
  def __init__(self, task, ssh_client):
    self.log = logging.getLogger(__name__)

    # make sure valid actions are selected `present` and `absent`
    if (task['module']['action'] in ['present', 'absent']):
      self.action = task['module']['action']
    else:
      msg = "Invalid actions were provided for % module, please correct them. Valid options are: `present` and `absent` " % (__name__)
      self.log.error(msg)
      raise Exception(msg)

    self.name = task['name']
    self.ssh_client = ssh_client
    self.src = task['module']['src']
    self.dest = task['module']['dest']
    self.dest_tmp = "/tmp/%s" % (os.path.basename(self.dest))
    self.owner = task['module']['owner']
    self.group = task['module']['group']
    self.mod = task['module']['mod']
    

  def file_exists(self):
    # use this function to guarantee indempotence
    cmd = "python -c \"exec(\\\"import os\\nprint os.path.isfile('%s')\\\")\"" % (self.dest)
    stdout, stderr = self.ssh_client.execute(cmd)

    # a return value of 1 means the package is present, 0 means its absent
    if ('True' in stdout[0]):
      return True
    else:
      return False


  def get_file_mod(self):
    cmd = "python -c \"exec(\\\"import os\\nprint oct(os.stat('%s').st_mode)[4:]\\\")\"" % (self.dest)
    stdout, stderr = self.ssh_client.execute(cmd)
    return int(stdout[0])


  def set_file_mod(self):
    cmd = "python -c \"exec(\\\"import os\\nos.chmod('%s', 0%d)\\\")\"" % (self.dest, int(self.mod))
    stdout, stderr = self.ssh_client.execute(cmd)


  def get_file_owner(self):
    cmd = "python -c \"exec(\\\"import os,pwd\\nprint pwd.getpwuid(os.stat('%s').st_uid).pw_name\\\")\"" % (self.dest)
    stdout, stderr = self.ssh_client.execute(cmd)
    return stdout[0]


  def set_file_owner(self):
    cmd = "python -c \"exec(\\\"import os,pwd\\nos.chown('%s', pwd.getpwnam('%s').pw_uid, -1)\\\")\"" % (self.dest, self.owner)
    stdout, stderr = self.ssh_client.execute(cmd)


  def get_file_group(self):
    cmd = "python -c \"exec(\\\"import os,grp\\nprint grp.getgrgid(os.stat('%s').st_gid).gr_name\\\")\"" % (self.dest)
    stdout, stderr = self.ssh_client.execute(cmd)
    return stdout[0]


  def set_file_group(self):
    cmd = "python -c \"exec(\\\"import os,grp\\nos.chown('%s', -1, grp.getgrnam('%s').gr_gid)\\\")\"" % (self.dest, self.group)
    stdout, stderr = self.ssh_client.execute(cmd)
  

  def remove_file(self, file_name):
    if (self.file_exists()):
      cmd = "python -c \"exec(\\\"import os,grp\\nos.remove('%s')\\\")\"" % (file_name)
      stdout, stderr = self.ssh_client.execute(cmd)
      return True
    else:
      return False, "UNCHANGED" # figure out something here


  def compare_dest_files(self):
    cmd = "python -c \"exec(\\\"import filecmp\\nprint filecmp.cmp('%s', '%s')\\\")\"" % (self.dest, self.dest_tmp)
    stdout, stderr = self.ssh_client.execute(cmd)

    if ('True' in stdout[0]):
      return True
    else:
      return False
    

  def execute_action(self):
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
              return False, "UNCHANGED"
          else:
            return False, "UNCHANGED" 
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
        return False, "UNCHANGED"
