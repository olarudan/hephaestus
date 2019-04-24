import sys
import os
import yaml

class Config:
  """ A class used to manage configuration for the hephaestus configuration management tool. """

  def __init__(self):
    dir = os.path.dirname(os.path.realpath(sys.argv[0]))

    # load config from yml file
    with open(os.path.join(dir, "config.yml"), 'r') as yml_file:
      self.cfg = yaml.load(yml_file)

  def get_config(self):
    """ Returns hepahestus configuration.

    Returns
    ------
    dict:
        configuration parameters and its values        
    """
    return self.cfg

config = Config().get_config()
