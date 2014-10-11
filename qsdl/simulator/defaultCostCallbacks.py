# -*- coding: latin-1 -*-
'''
Created on 3.10.2012

@author: Teemu Pääkkönen
'''

def get_callback_map():

  AVG_AUTOCOMPLETE_INPUT_LENGTH = 5

  def get_current_query_cost( simulation, key_cost, interaction_type = "basic" ):
    if "basic" == interaction_type:
      return float(key_cost) * len( simulation.get_current_query_text() )
    elif "autocomplete" == interaction_type:
      return float(key_cost) * AVG_AUTOCOMPLETE_INPUT_LENGTH

  return { 'get_default_current_query_cost': get_current_query_cost }
