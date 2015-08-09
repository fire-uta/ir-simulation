# -*- coding: latin-1 -*-
'''
Created on 27.9.2012

@author: Teemu Pääkkönen
'''

from qsdl.simulator.events import DocumentChanged

def get_callback_map():

    def trigger_next_document( simulation ):
        simulation.increment_current_state_rank()
        simulation.notifyObservers( DocumentChanged(
            simulation.currentState, simulation.get_current_document_id() ) )

    def trigger_new_query( simulation, qidx ):
        simulation.set_current_state_query_index( qidx )

    def trigger_next_query( simulation ):
        simulation.increment_current_state_query_index()
        simulation.reset_current_query_rank()
        simulation.reset_current_query_cumulated_gain()
        simulation.reset_current_query_documents_seen()

    def flag_as_seen( simulation ):
        simulation.flag_current_document_as_seen()

    triggers = {
                    'nextDocument': trigger_next_document,
                    'jumpToQuery': trigger_new_query,
                    'nextQuery': trigger_next_query,
                    'flagAsSeen': flag_as_seen
               }

    return triggers
