import sys
import os
import yaml

class Config:
  def __init__(self):
    dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    print dir

    # load config from yml file
    with open(os.path.join(dir, "config.yml"), 'r') as yml_file:
      self.cfg = yaml.load(yml_file)

  def get_config(self):
    return self.cfg

config = Config().get_config()
