# -*- coding: latin-1 -*-
'''
Created on 6.11.2012

@author: Teemu Pääkkönen
'''

import optparse

def get_config_file_name():
    cliParser = optparse.OptionParser()
    (options, args) = cliParser.parse_args()
    configName = 'config.xml' if len(args) < 1 else args[0]
    return configName
