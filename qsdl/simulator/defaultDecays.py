# -*- coding: latin-1 -*-
'''
Created on 31.10.2012

@author: Teemu Pääkkönen
'''

def get_callback_map():
    
    def calculate_frustration( simulation, maxCost, strength ):
        return (simulation.get_current_cumulated_cost() / float(maxCost)) * float(strength)

    return { 'calculate_frustration': calculate_frustration }