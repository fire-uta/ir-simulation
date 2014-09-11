# -*- coding: latin-1 -*-
'''
Created on 11.10.2012

@author: Teemu Pääkkönen
'''

def get_callback_map():

    def generate_negation_function( function ):
        return lambda simulation, negation, **kwargs: function( simulation, **kwargs ) ^ negation

    conditions = { 'default_current_document_is_relevant':
            lambda simulation, min_relevance:
                (float(simulation.get_current_document_relevance_level()) >= float(min_relevance)),

            'default_current_document_is_last_on_page':
            lambda simulation:
                (simulation.get_current_query_rank() % simulation.get_page_size() == 0),

            'default_current_document_is_ranked_last':
            lambda simulation:
                (simulation.get_current_query_rank() == simulation.get_current_results_length()),

            'default_current_query_is_last':
            lambda simulation:
                (simulation.current_query_is_last_query()),

            'default_gain_exceeded':
            lambda simulation, gain_limit:
                (simulation.currentState.cumulatedGain > float(gain_limit)),

            'default_cost_exceeded':
            lambda simulation, cost_limit:
                (simulation.currentState.cumulatedCost > float(cost_limit)),

            'default_total_rank_exceeded':
            lambda simulation, rank_limit:
                (simulation.get_current_total_rank() > int(rank_limit)),

            'default_query_rank_exceeded':
            lambda simulation, rank_limit:
                (simulation.get_current_query_rank() > int(rank_limit)) }

    negations = {}
    for condition in conditions.iterkeys():
        negations[ condition ] = generate_negation_function( conditions[ condition ] )
    return negations
