import pytest

from hephaestus.config import Config

def test_config_without_manifest_file():
  """ The program will throw and exception if the configuration file is misconfigured """
  with pytest.raises(Exception):
    test_config = Config("examples/config/bad.config.yml") 
