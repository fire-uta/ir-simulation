# -*- coding: latin-1 -*-
'''
Created on 16.10.2012

@author: Teemu Pääkkönen
'''

import imp
import sys
import os
import ntpath

from qsdl.simulator.errors.ConfigurationInvalidError import ConfigurationInvalidError


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def get_callback_module( name ):

    scriptDir = os.path.dirname(os.path.realpath(__file__))
    callback_module_dir = scriptDir + '/' + ntpath.dirname( name )
    callback_module_name = path_leaf( name )

    # Already loaded?
    try:
        return sys.modules[name]
    except KeyError:
        pass

    fp = pathname = description = None
    try:
        fp, pathname, description = imp.find_module(callback_module_name, [callback_module_dir, os.getcwdu(), scriptDir])
        return imp.load_module(name, fp, pathname, description)
    except:
        return None
    finally:
        if fp:
            fp.close()
