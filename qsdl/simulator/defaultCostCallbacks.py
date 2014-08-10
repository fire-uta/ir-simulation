# -*- coding: latin-1 -*-
'''
Created on 3.10.2012

@author: Teemu Pääkkönen
'''

def get_callback_map():
    
    def get_current_query_cost( simulation, key_cost ):
        return float(key_cost) * len( simulation.get_current_query_text() )

    return { 'get_default_current_query_cost': get_current_query_cost }