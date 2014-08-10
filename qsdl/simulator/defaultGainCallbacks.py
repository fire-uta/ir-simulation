# -*- coding: latin-1 -*-
'''
Created on 4.10.2012

@author: Teemu Pääkkönen
'''

def get_callback_map():
    
    def get_current_document_gain( simulation ):
        if not simulation.current_document_has_been_seen():
            return simulation.get_current_document_gain()
        return 0

    return { 'get_current_document_gain': get_current_document_gain }