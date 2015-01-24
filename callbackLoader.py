# -*- coding: latin-1 -*-
'''
Created on 16.10.2012

@author: Teemu Pääkkönen
'''

import imp
import sys
import os

from qsdl.simulator.errors.ConfigurationInvalidError import ConfigurationInvalidError

def get_callback_module( name ):

    # Already loaded?
    try:
        return sys.modules[name]
    except KeyError:
        pass

    fp = pathname = description = None

    try:
        fp, pathname, description = imp.find_module(name, [os.getcwdu()])
        return imp.load_module(name, fp, pathname, description)
    except ImportError as e:
        raise ConfigurationInvalidError("Callback file not found: %s" % name)
    except:
        return None
    finally:
        if fp:
            fp.close()


