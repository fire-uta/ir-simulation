# -*- coding: latin-1 -*-
'''
Created on 16.10.2012

@author: Teemu Pääkkönen
'''

import stats as stats

def get_output_formatter( config, sessionId ):
    # Python style output formatter.
    
    def set_up():
        return 'history = {}' + '\n' + 'seed = {}'
    
    def handle_history( simulations ):
        first = simulations[0]
        sessId = first.get_session_id()
        return 'history[' + repr( sessId ) + '] = ' + repr( simulations )
    
    def handle_stats( runs ):
        return 'avgGainsRank = ' + repr(stats.get_average_cumulated_gains_at_total_rank_range( runs )) + '\n' \
        + 'maxGainsRank = ' + repr(stats.get_max_cumulated_gains_at_total_rank_range( runs )) + '\n' \
        + 'minGainsRank = ' + repr(stats.get_min_cumulated_gains_at_total_rank_range( runs )) + '\n' \
        + 'avgGainsCost = ' + repr(stats.get_average_cumulated_gains_at_cost_range( runs, 10 )) + '\n' \
        + 'maxGainsCost = ' + repr(stats.get_max_cumulated_gains_at_cost_range( runs, 10 )) + '\n' \
        + 'minGainsCost = ' + repr(stats.get_min_cumulated_gains_at_cost_range( runs, 10 )) + '\n' \
        + 'avgCostsRank = ' + repr(stats.get_average_cumulated_costs_at_total_rank_range( runs )) + '\n' \
        + 'maxCostsRank = ' + repr(stats.get_max_cumulated_costs_at_total_rank_range( runs )) + '\n' \
        + 'minCostsRank = ' + repr(stats.get_min_cumulated_costs_at_total_rank_range( runs )) + '\n' \
        + 'avgTotalRank = ' + repr(stats.get_average_total_rank(runs)) + '\n' \
        + 'avgGain = ' + repr(stats.get_average_cumulated_gain(runs)) + '\n' \
        + 'avgCost = ' + repr(stats.get_average_cumulated_cost(runs)) + '\n' \
        + 'maxTotalRank = ' + repr(stats.get_max_total_rank(runs)) + '\n' \
        + 'maxGain = ' + repr(stats.get_max_cumulated_gain(runs)) + '\n' \
        + 'maxCost = ' + repr(stats.get_max_cumulated_cost(runs)) + '\n' \
        + 'minTotalRank = ' + repr(stats.get_min_total_rank(runs)) + '\n' \
        + 'minGain = ' + repr(stats.get_min_cumulated_gain(runs)) + '\n' \
        + 'minCost = ' + repr(stats.get_min_cumulated_cost(runs)) + '\n' \
        + 'varTotalRank = ' + repr(stats.get_total_rank_variance(runs)) + '\n' \
        + 'varGain = ' + repr(stats.get_cumulated_gain_variance(runs)) + '\n' \
        + 'varCost = ' + repr(stats.get_cumulated_cost_variance(runs))
        
    def handle_seed( seed ):
        return 'seed = ' + repr( seed )
        
    def handle_input_files( configFileName, simulationFileName ):
        return 'config = ' + repr( configFileName ) + '\n' + \
            'simulation = ' + repr( simulationFileName )
        
    def get_file_mode():
        return 'w'
    
    return {
            'format_history': handle_history,
            'format_stats': handle_stats,
            'format_seed': handle_seed,
            'set_up': set_up,
            'format_input_files': handle_input_files,
            'get_file_mode': get_file_mode
            }
    
