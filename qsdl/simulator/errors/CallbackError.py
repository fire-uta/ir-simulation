# -*- coding: latin-1 -*-
'''
Created on 5.11.2012

@author: Teemu P��kk�nen
'''

from qsdl.simulator.errors.IrsimError import IrsimError

class CallbackError(IrsimError):

    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return repr( self.value )
    
    
        