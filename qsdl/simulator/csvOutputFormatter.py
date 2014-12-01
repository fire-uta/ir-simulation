# -*- coding: latin-1 -*-
'''
Created on 17.10.2012

@author: Teemu Pääkkönen
'''

import csv
import cStringIO
import io
import stats as stats
from qsdl.simulator.simulation import SimulationState

def get_output_formatter( config, sessionId ):
    # CSV output formatter.

    def set_up():
        output = io.BytesIO()
        writer = csv.writer( output )
        heading = SimulationState.get_field_order( False )
        heading.extend( config.get_derived_gains_dict( sessionId ).keys() )
        writer.writerow( heading )
        return output.getvalue()

    def handle_history( simulations ):
        output = cStringIO.StringIO()
        writer = csv.writer( output )
        for simulation in simulations:
            for state in simulation.history:
                derivedGains = state.get_derived_gains()
                stateAsList = [ state.__dict__.get( key ) for key in \
                    SimulationState.get_field_order( False ) ]
                stateAsList.extend( [ derivedGains.get( key ) for key in \
                    config.get_derived_gains_dict( sessionId ).keys() ] )
                writer.writerow( stateAsList )
        return output.getvalue()

    def handle_stats( runs ):
        output = cStringIO.StringIO()
        writer = csv.writer( output )

        def catWrite(listA,listB):
            copy = listA[:]
            copy.extend( listB )
            writer.writerow( copy )

        catWrite( [ 'rank' ], stats.get_max_rank_range( runs ) )
        catWrite( [ 'amt runs' ], stats.get_amount_of_runs_at_total_rank_range( runs ) )
        catWrite( [ 'avg gain' ], stats.get_average_cumulated_gains_at_total_rank_range( runs ) )
        catWrite( [ 'max gain' ], stats.get_max_cumulated_gains_at_total_rank_range( runs ) )
        catWrite( [ 'min gain' ], stats.get_min_cumulated_gains_at_total_rank_range( runs ) )
        catWrite( [ 'avg cost' ], stats.get_average_cumulated_costs_at_total_rank_range( runs ) )
        catWrite( [ 'max cost' ], stats.get_max_cumulated_costs_at_total_rank_range( runs ) )
        catWrite( [ 'min cost' ], stats.get_min_cumulated_costs_at_total_rank_range( runs ) )
        writer.writerow([])

        costInterval = 10
        catWrite( [ 'cost' ], stats.get_min_cost_range( runs, costInterval ) )
        catWrite( [ 'amt runs' ], stats.get_amount_of_runs_at_cost_range( runs, costInterval ) )
        catWrite( [ 'avg gain' ], stats.get_average_cumulated_gains_at_cost_range( runs, costInterval ) )
        catWrite( [ 'max gain' ], stats.get_max_cumulated_gains_at_cost_range( runs, costInterval ) )
        catWrite( [ 'min gain' ], stats.get_min_cumulated_gains_at_cost_range( runs, costInterval ) )
        writer.writerow([])

        writer.writerow( [ 'avgTotalRank', stats.get_average_total_rank(runs)] )
        writer.writerow( [ 'avgGain', stats.get_average_cumulated_gain(runs)] )
        writer.writerow( [ 'avgCost', stats.get_average_cumulated_cost(runs)] )
        writer.writerow( [ 'maxTotalRank', stats.get_max_total_rank(runs)] )
        writer.writerow( [ 'maxGain', stats.get_max_cumulated_gain(runs)] )
        writer.writerow( [ 'maxCost', stats.get_max_cumulated_cost(runs)] )
        writer.writerow( [ 'minTotalRank', stats.get_min_total_rank(runs)] )
        writer.writerow( [ 'minGain', stats.get_min_cumulated_gain(runs)] )
        writer.writerow( [ 'minCost', stats.get_min_cumulated_cost(runs)] )
        writer.writerow( [ 'varTotalRank', stats.get_total_rank_variance(runs)] )
        writer.writerow( [ 'varGain', stats.get_cumulated_gain_variance(runs)] )
        writer.writerow( [ 'varCost', stats.get_cumulated_cost_variance(runs)] )

        return output.getvalue()

    def handle_seed( seed ):
        # No seed printed in CSV format
        return ''

    def handle_input_files( configFileName, simulationFileName ):
        # No input file names printed in CSV format
        return ''

    def get_file_mode():
        return 'wb'

    return {
            'format_history': handle_history,
            'format_stats': handle_stats,
            'format_seed': handle_seed,
            'set_up': set_up,
            'format_input_files': handle_input_files,
            'get_file_mode': get_file_mode
            }

def get_cross_session_output_formatter( config ):

    def handle_cross_session_stats( sessions ):
        output = cStringIO.StringIO()
        writer = csv.writer( output )

        def catWrite(listA,listB):
            copy = listA[:]
            copy.extend( listB )
            writer.writerow( copy )

        catWrite( [ 'rank' ], stats.get_max_cross_session_rank_range( sessions ) )
        catWrite( [ 'avg amt runs' ], stats.get_average_amount_of_runs_at_total_rank_range( sessions ) )
        catWrite( [ 'avg gain' ], stats.get_average_cross_session_cumulated_gains_at_total_rank_range( sessions ) )
        catWrite( [ 'avg cost' ], stats.get_average_cross_session_cumulated_costs_at_total_rank_range( sessions ) )
        catWrite( [ 'avg gain SD' ], stats.get_cross_session_cumulated_gain_stddevs_at_total_rank_range( sessions ) )
        writer.writerow([])

        costInterval = 10
        catWrite( [ 'cost' ], stats.get_min_cross_session_cost_range( sessions, costInterval ) )
        catWrite( [ 'avg amt runs' ], stats.get_average_amount_of_runs_at_cost_range( sessions, costInterval ) )
        catWrite( [ 'avg gain' ], stats.get_average_cross_session_cumulated_gains_at_cost_range( sessions, costInterval ) )
        catWrite( [ 'avg gain SD' ], stats.get_average_cross_session_cumulated_gain_stddevs_at_cost_range( sessions, costInterval ) )
        writer.writerow([])

        return output.getvalue()

    def get_file_mode():
        return 'wb'

    return {
            'format_cross_session_stats': handle_cross_session_stats,
            'get_file_mode': get_file_mode
            }
