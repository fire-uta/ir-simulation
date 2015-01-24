# -*- coding: latin-1 -*-
'''
Created on 6.11.2012

@author: Teemu Pääkkönen
'''

import optparse

class CLIParser: pass

CLIParser.parser = optparse.OptionParser()
CLIParser.parser.add_option("-o", "--out", metavar="DIR", help="Write all output to DIR")
CLIParser.parsedArgs = CLIParser.parser.parse_args()

def get_args():
  (options, args) = CLIParser.parsedArgs
  return args


def get_options():
  (options, args) = CLIParser.parsedArgs
  return options


def get_config_file_name():
  args = get_args()
  configName = 'config.xml' if len(args) < 1 else args[0]
  return configName


def get_output_directory():
  options = get_options()
  return options.out
