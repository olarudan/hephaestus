from hephaestus.config import config
import paramiko
import logging
import sys
import pprint

class SSH:
  def __init__(self, hostname):
    self.hostname = hostname
    self.username = config['ssh']['username'] 
    self.password = config['ssh']['password']
    self.log = logging.getLogger(__name__)

  def connect(self):
    try:
      self.ssh_client = paramiko.SSHClient()
      self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      self.ssh_client.connect(hostname=self.hostname, username=self.username, password=self.password, look_for_keys=False, allow_agent=False)
      self.log.info('Created the SSH connection successfully')
    except:
      self.log.error('Failed to create the SSH connection. Please check your username/password/host.')
      sys.exit(1)

  def execute(self, command):
    try:
      stdin, stdout, stderr = self.ssh_client.exec_command("DEBIAN_FRONTEND=noninteractive %s" % (command))

      # read stdout && stderr values    
      stdout = stdout.readlines()
      stderr = stderr.readlines()
   
      if (stderr != []): # exit when there is an error
        self.log.error("SSH command `%s` returned an error:\n%s" % (command, ' '.join(stderr)))
        sys.exit(1)
    
      self.log.info("SSH command: `%s` executed successfully:\n%s" % (command, ' '.join(stdout)))

    except Exception as e:
      self.log.error('Failed to run command `%s` through the SSH connection. \nException: %s' % (command, e))
      sys.exit(1)

    return stdout, stderr

  def copy_file(self, src, dest):
    try:
      ftp_client=self.ssh_client.open_sftp()
      ftp_client.put(src, dest)
      ftp_client.close() 
      self.log.info("Copied `%s` to `%s` successfully" % (src, dest))
    except Exception as e:
      self.log.error('Failed to copy `%s` to `%s`. Make sure your source file exists(relative to hephaestus source code dir, same goes for the destination dir. \nException: %s' % (src, dest, e))
      sys.exit(1)
    finally:
      ftp_client.close()
