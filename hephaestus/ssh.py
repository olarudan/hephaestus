from hephaestus.config import config
import paramiko

class SSH:
  def __init__(self, hostname):
    self.hostname = hostname
    self.username = config['ssh']['username'] 
    self.password = config['ssh']['password']

  def connect(self):
    try:
      self.ssh_client = paramiko.SSHClient()
      self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      self.ssh_client.connect(hostname=self.hostname, username=self.username, password=self.password)
      # log successfull connection
    except:
      #log something bad here
      print('something went wrong')

  def execute(self, command):
    stdin,stdout,stderr=self.ssh_client.exec_command(command)
    print(stdout.readlines())
    # log here
