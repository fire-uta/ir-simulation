# -*- coding: latin-1 -*-
'''
Created on 1.11.2012

@author: Teemu Pääkkönen
'''

from qsdl.simulator.errors.IrsimError import IrsimError

class UnknownDocumentError(IrsimError):

    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return repr( self.value )
    
    
        