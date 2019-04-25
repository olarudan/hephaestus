import sys
import os
import yaml
import argparse

class Config:
  """ A class used to manage configuration for the hephaestus configuration management tool. """

  def __init__(self):
    
    # parse cli arguments
    self.parser = argparse.ArgumentParser(description = 'Execute hep manifests against remote hosts')
    self.parser.add_argument('manifest', nargs='*',  help = 'Manifest file to run')
    self.parser.add_argument('--hosts', '-i', help = 'Hosts file to use')
    self.parser.add_argument('--config', '-c', help = 'Config file to use')
    self.args = self.parser.parse_args()

    # override config file path if passed through clid
    if (self.args.config == None):
      # by default hep will look in the current working dir for a config.yml file
      #dir = os.path.dirname(os.path.realpath(sys.argv[0]))
      dir = os.getcwd()
      config_file_path = os.path.join(dir, "config.yml")
    else:
      config_file_path = os.path.realpath(self.args.config)

    # load config from yml file
    with open(config_file_path, 'r') as yml_file:
      self.cfg = yaml.load(yml_file)

    # override manifest file path if passed through cli
    if (self.args.manifest != []):
      # by default hep will look for the manifest file path in config file
      self.cfg['manifest'] = self.args.manifest[0]

    # override hosts file path if passed through cli
    if (self.args.hosts != None):
      # by default hep will look for the hosts file path in config file
      self.cfg['hosts'] = self.args.hosts

  def get_config(self):
    """ Returns hepahestus configuration.

    Returns
    ------
    dict:
        configuration parameters and its values        
    """
    return self.cfg

config = Config().get_config()
