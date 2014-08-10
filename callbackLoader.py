# -*- coding: latin-1 -*-
'''
Created on 16.10.2012

@author: Teemu Pääkkönen
'''

import imp
import sys
import os

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
    except:
        return None
    finally:
        if fp:
            fp.close()
            
            