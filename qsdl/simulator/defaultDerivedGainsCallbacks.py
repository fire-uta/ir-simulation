# -*- coding: latin-1 -*-
'''
Created on 29.10.2012

@author: Teemu Pääkkönen
'''

import math

def get_callback_map():
    
    def calc_dcg( simulation, base ):
        if not simulation.current_document_has_been_seen():
            discountFactor = 1 + simulation.get_current_total_rank()
            return simulation.get_current_document_gain()/math.log(discountFactor,float(base))
        return 0

    return { 'calc_dcg': calc_dcg }
