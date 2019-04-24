from hephaestus.config import config
import paramiko
import logging
import sys
import pprint

class SSH:
  """
  A class used to manage ssh connections, execute commands over ssh and copy files 
  using the paramiko library.

  Attributes
  ----------
  hostname : str
      the hostname to create ssh connection with

  Methods
  -------
  connect()
      creates the ssh connection
  execute(command)
      executes shell commands on a remote host over ssh
  close()
      closes the ssh connection
  copy_file(src, dest)
      copies a local file to a remote host over sftp
  """

  def __init__(self, hostname):
    """
    Parameters
    ----------
    hostname : str
        hostname of the remote machine
    username : str
        remote machine's username
    password : str
        remote machine's password
    log : 
        logging object used to collect logs
    """
    self.hostname = hostname
    self.username = config['ssh']['username'] 
    self.password = config['ssh']['password']
    self.log = logging.getLogger(__name__)

  def connect(self):
    """ Creates a ssh connection with the remote host. 
    
    If it can't establish an ssh connection it will log the error and exit with a status code of 1.
    """

    try:
      self.ssh_client = paramiko.SSHClient()
      self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      self.ssh_client.connect(hostname=self.hostname, username=self.username, password=self.password, look_for_keys=False, allow_agent=False)
      self.log.info('Created the SSH connection successfully')
    except:
      self.log.error('Failed to create the SSH connection. Please check your username/password/host.')
      sys.exit(1)

  def execute(self, command):
    """ Execute a command on the remote host. 
    
    If the command returns a non-empty stderr object then the program exit with a status code of 1.
    Sometimes commands return non-empty stderr and stdout. The program will assume that the command executed
    correctly as is the case with `apt-get install php5` on a debian distro. It does just that but installs
    the package correctly.

    Parameters
    ----------
    command : str
        The command to be executed on the remote host. I.e. `ls`.

    Returns
    ------
    tuple:
        stdout is the first value in the tuple and contains a string of the command's stdout.
        stderr is the second value in the tuple and contains a string of the command's stderr
    """
    try:
      stdin, stdout, stderr = self.ssh_client.exec_command(command)

      # read stdout && stderr values    
      stdout = stdout.readlines()
      stderr = stderr.readlines()
      
      # assume that if both stderr and stdout are not empty then there is no real error
      if (stderr != [] and stdout == []): # exit when there is an error
        msg = "SSH command `%s` returned an error:\n%s" % (command, ' '.join(stderr))
        self.log.error(msg)
        print(msg)
        sys.exit(1)
      else:
        self.log.info("SSH command: `%s` executed successfully:\n%s" % (command, ' '.join(stdout)))

    except Exception as e:
      self.log.error('Failed to run command `%s` through the SSH connection. \nException: %s' % (command, e))
      sys.exit(1)

    return stdout, stderr

  def close(self):
    """ Closes the ssh connection. """    

  def copy_file(self, src, dest):
    """ Copies a file from the local host to the remote host over sftp.
    
    The program will exit with a exit code of `1` if it can't copy the file successfully.
    
    Parameters
    ----------
    command : str
        The command to be executed on the remote host. I.e. `ls`.
    """

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
