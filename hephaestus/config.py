import sys, os, yaml

class Config:
  def __init__(self):
    dir = os.path.dirname(os.path.realpath(sys.argv[0]))

    # get general config
    with open(os.path.join(dir, "config.yml"), 'r') as ymlfile:
      self.cfg = yaml.load(ymlfile)

  def get_config(self):
    return self.cfg
