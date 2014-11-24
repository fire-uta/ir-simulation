# -*- coding: latin-1 -*-
'''
Created on 6.11.2012

@author: Teemu Pääkkönen
'''

import inspect
import math

class Stats: pass

def get_caller_function_name():
    callerLocationInStack = 3
    return get_function_name(callerLocationInStack)

def get_function_name( functionStackLocation = 1 ):
    functionNameIndex = 3
    try:
        return inspect.stack()[functionStackLocation][functionNameIndex]
    except:
        return None

def set_if_not_exist_and_get( dict_, id_, setFunc ):
    if not dict_.has_key( id_ ):
        dict_[ id_ ] = setFunc()
    return dict_[ id_ ]

def init_dict_if_not_exist( dict_, id_ ):
    set_if_not_exist_and_get( dict_, id_, lambda : {} )

def init_dict_and_set( dict_, ids, setFunc ):
    if len( ids ) == 1:
        return set_if_not_exist_and_get( dict_, ids[ 0 ], setFunc )
    else:
        init_dict_if_not_exist( dict_, ids[0] )
        return init_dict_and_set( dict_[ ids[0] ], ids[1:], setFunc )

def calc_and_get( name, ids, setFunc ):
    init_dict_if_not_exist( Stats.__dict__, name )
    return init_dict_and_set( Stats.__dict__[ name ], ids, setFunc )

def calc_and_get_by_fname( ids, setFunc ):
    name = get_caller_function_name()
    return calc_and_get( name, ids, setFunc )

def get_final_states( runs ):
    return calc_and_get( 'finalStates', [ id(runs) ],
                         lambda : [ run.history[ -1 ] for run in runs ] )

def get_final_gains( runs ):
    return calc_and_get( 'finalGains', [ id(runs) ],
                         lambda : [ float(state.cumulatedGain) for state in get_final_states(runs) ] )

def get_final_costs( runs ):
    return calc_and_get( 'finalCosts', [ id(runs) ],
                         lambda : [ float(state.cumulatedCost) for state in get_final_states(runs) ] )

def get_final_total_ranks( runs ):
    return calc_and_get( 'finalTotalRanks', [ id(runs) ],
                         lambda : [ float(state.totalRank) for state in get_final_states(runs) ] )

def get_final_cross_session_total_ranks( sessions ):
    return calc_and_get_by_fname( [ id(sessions) ],
                         lambda : [ max(get_final_total_ranks( runs )) for runs in sessions ] )

def get_last_states_at_total_rank( runs, rank ):
    return calc_and_get( 'lastStatesAtRank', [ id(runs), rank ],
                         lambda : [ run.get_last_state_at_total_rank( rank ) for run in runs ] )

def get_gains_at_total_rank( runs, rank ):
    def get_gains():
        gains = []
        amtNones = 0
        for state in get_last_states_at_total_rank(runs,rank):
            if state != None:
                gains.append( float( state.cumulatedGain ) )
            else:
                amtNones += 1
        return (gains,amtNones)

    return calc_and_get( 'gainsAtTotalRank', [ id(runs), rank ], get_gains )

def get_derived_gains_at_total_rank( gainId, runs, rank  ):
    def get_gains():
        gains = []
        for state in get_last_states_at_total_rank(runs,rank):
            if state != None:
                gains.append( float( state.gains[ gainId ] ) )
        return gains

    return calc_and_get_by_fname( [ id(runs), rank, gainId ], get_gains )

def get_sorted_gains_at_total_rank( runs, rank ):
    def get_gains():
        (gains,amtNones) = get_gains_at_total_rank( runs, rank )
        return (sorted( gains ), amtNones)
    return calc_and_get_by_fname( [id(runs), rank], get_gains )

def get_sorted_derived_gains_at_total_rank( gainId, runs, rank ):
    def get_gains():
        gains = get_derived_gains_at_total_rank( gainId, runs, rank )
        return sorted( gains )
    return calc_and_get_by_fname( [gainId, id(runs), rank], get_gains )

def get_sorted_costs_at_total_rank( runs, rank ):
    def get_gains():
        (costs,amtNones) = get_costs_at_total_rank( runs, rank )
        return (sorted( costs ), amtNones)
    return calc_and_get_by_fname( [id(runs), rank], get_gains )

def get_top_gains_at_total_rank( runs, rank, proportion = 25, bottom = False ):
    def get_gains():
        (gains,amtNones) = get_sorted_gains_at_total_rank( runs, rank )
        numItems = int( math.ceil( (proportion/100.0) * len( gains ) ) )
        return gains[:numItems] if bottom else gains[-numItems:]

    return calc_and_get_by_fname( [id(runs), rank, proportion, bottom], get_gains )

def get_top_derived_gains_at_total_rank( gainId, runs, rank, proportion = 25, bottom = False ):
    def get_gains():
        gains = get_sorted_derived_gains_at_total_rank( gainId, runs, rank )
        numItems = int( math.ceil( (proportion/100.0) * len( gains ) ) )
        return gains[:numItems] if bottom else gains[-numItems:]

    return calc_and_get_by_fname( [gainId, id(runs), rank, proportion, bottom], get_gains )

def get_top_gains_at_cost( runs, cost, proportion = 25, bottom = False ):
    def get_gains():
        (gains,amtNones) = get_sorted_gains_at_cost( runs, cost )
        numItems = int( math.ceil( (proportion/100.0) * len( gains ) ) )
        return gains[:numItems] if bottom else gains[-numItems:]
    return calc_and_get_by_fname( [id(runs), cost, proportion, bottom], get_gains )

def get_top_derived_gains_at_cost( gainId, runs, cost, proportion = 25, bottom = False ):
    def get_gains():
        gains = get_sorted_derived_gains_at_cost( gainId, runs, cost )
        numItems = int( math.ceil( (proportion/100.0) * len( gains ) ) )
        return gains[:numItems] if bottom else gains[-numItems:]
    return calc_and_get_by_fname( [gainId, id(runs), cost, proportion, bottom], get_gains )

def get_costs_at_total_rank( runs, rank ):
    def get_costs():
        costs = []
        amtNones = 0
        for state in get_last_states_at_total_rank(runs,rank):
            if state != None:
                costs.append( float( state.cumulatedCost ) )
            else:
                amtNones += 1
        return (costs,amtNones)
    return calc_and_get( 'costsAtTotalRank', [ id(runs), rank ], get_costs )

def get_top_costs_at_total_rank( runs, rank, proportion = 25, bottom = False ):
    def get_gains():
        (costs,amtNones) = get_sorted_costs_at_total_rank( runs, rank )
        numItems = int( math.ceil( (proportion/100.0) * len( costs ) ) )
        return costs[:numItems] if bottom else costs[-numItems:]
    return calc_and_get_by_fname( [id(runs), rank, proportion, bottom], get_gains )

def get_gains_at_cost( runs, cost ):
    def get_gains():
        gains = []
        amtNones = 0
        for run in runs:
            state = run.get_first_state_at_cost( cost )
            if state != None:
                gains.append( float( state.cumulatedGain ) )
            else:
                amtNones += 1
        return (gains,amtNones)
    return calc_and_get( 'gainsAtCost', [ id(runs), cost ], get_gains )

def get_derived_gains_at_cost( gainId, runs, cost ):
    def get_gains():
        gains = []
        for run in runs:
            state = run.get_first_state_at_cost( cost )
            if state != None:
                gains.append( float( state.gains[ gainId ] ) )
        return gains
    return calc_and_get_by_fname( [ gainId, id(runs), cost ], get_gains )

def get_sorted_gains_at_cost( runs, cost ):
    def get_gains():
        (gains,amtNones) = get_gains_at_cost( runs, cost )
        return (sorted( gains ), amtNones)
    return calc_and_get_by_fname( [ id(runs), cost ], get_gains )

def get_sorted_derived_gains_at_cost( gainId, runs, cost ):
    def get_gains():
        gains = get_derived_gains_at_cost( gainId, runs, cost )
        return sorted( gains )
    return calc_and_get_by_fname( [ gainId, id(runs), cost ], get_gains )

def get_average_cumulated_gain( runs ):
    return calc_and_get( 'avgGains', [ id(runs) ],
                         lambda : sum( get_final_gains(runs) )/float(len(runs)) )

def get_average_total_rank( runs ):
    return calc_and_get( 'avgTotalRanks', [ id(runs) ],
                         lambda : sum( get_final_total_ranks(runs) )/float(len(runs)) )

def get_average_cumulated_gain_at_total_rank( runs, rank ):
    def getAvgGain():
        gains,amtNones = get_gains_at_total_rank(runs,rank)
        amtRuns = len(runs)
        return float(sum( gains ))/float(amtRuns - amtNones)
    return calc_and_get( 'avgGainsAtRank', [ id(runs), rank ], getAvgGain )

def get_average_derived_gain_at_total_rank( gainId, runs, rank ):
    def getAvgGain():
        gains = get_derived_gains_at_total_rank(gainId,runs,rank)
        return float(sum( gains ))/float(len(gains))
    return calc_and_get_by_fname( [ id(runs), rank, gainId ], getAvgGain )

def get_average_top_cumulated_gain_at_total_rank( runs, rank, proportion = 25, bottom = False):
    def getAvgGain():
        gains = get_top_gains_at_total_rank(runs,rank, proportion, bottom)
        return float(sum( gains ))/float(len(gains))
    return calc_and_get_by_fname( [ id(runs), rank, proportion, bottom ], getAvgGain )

def get_average_top_derived_gain_at_total_rank( gainId, runs, rank, proportion = 25, bottom = False):
    def getAvgGain():
        gains = get_top_derived_gains_at_total_rank(gainId, runs,rank, proportion, bottom)
        return float(sum( gains ))/float(len(gains))
    return calc_and_get_by_fname( [ gainId, id(runs), rank, proportion, bottom ], getAvgGain )

def get_min_rank_range( runs, increment = 1 ):
    return calc_and_get( 'minTotalRankRanges', [ id(runs), increment ],
                         lambda : range(1, int(get_min_total_rank(runs)), increment) )

def get_max_rank_range( runs, increment = 1 ):
    return calc_and_get( 'maxTotalRankRanges', [ id(runs), increment ],
                         lambda : range(1, int(get_max_total_rank(runs)), increment) )

def get_max_cross_session_rank_range( sessions, increment = 1 ):
    return calc_and_get_by_fname( [ id(sessions), increment ],
                         lambda : range(1, int(get_max_cross_session_total_rank(sessions)), increment) )

def get_min_cost_range( runs, increment ):
    return calc_and_get( 'minCostRanges', [ id(runs), increment ],
                         lambda : range(0, int(get_min_cumulated_cost(runs)), increment) )

def get_min_cross_session_cost_range( sessions, increment ):
    return calc_and_get_by_fname( [ id(sessions), increment ],
                         lambda : range(0, int(get_min_cross_session_cumulated_cost(sessions)), increment) )

def get_max_cost_range( runs, increment ):
    return calc_and_get( 'maxCostRanges', [ id(runs), increment ],
                         lambda : range(0, int(get_max_cumulated_cost(runs)), increment) )

def get_cumulated_gain_stddevs_at_total_rank_range( runs, increment = 1 ):
    return calc_and_get( 'gainStddevsAtRankRanges', [ id(runs), increment ],
                         lambda : [ get_cumulated_gain_stddev_at_rank(runs, rank) for rank in get_max_rank_range(runs,increment) ] )

def get_avg_cumulated_gain_plusSD_at_total_rank_range( runs, factor = 1.0, increment = 1 ):
    return calc_and_get( 'avgGainPlus1SDAtRankRanges', [ id(runs), increment, factor ],
                         lambda : [ get_average_cumulated_gain_at_total_rank(runs, rank) + \
                                   factor * get_cumulated_gain_stddev_at_rank(runs, rank) for rank in get_max_rank_range(runs,increment) ] )

def get_avg_derived_gain_plusSD_at_total_rank_range( gainId, runs, factor = 1.0, increment = 1 ):
    return calc_and_get_by_fname( [ gainId, id(runs), increment, factor ],
                         lambda : [ get_average_derived_gain_at_total_rank(gainId, runs, rank) + \
                                   factor * get_derived_gain_stddev_at_rank(gainId, runs, rank) for rank in get_max_rank_range(runs,increment) ] )

def get_cumulated_gain_stddevs_at_cost_range( runs, increment ):
    return calc_and_get_by_fname( [ id(runs), increment ],
                         lambda : [ get_cumulated_gain_stddev_at_cost(runs, cost) for cost in get_max_cost_range(runs,increment) ] )

def get_avg_cumulated_gain_plusSD_at_cost_range( runs, increment, factor = 1.0 ):
    return calc_and_get_by_fname( [ id(runs), increment, factor ],
                         lambda : [ get_average_cumulated_gain_at_cost(runs, cost) + \
                                   factor * get_cumulated_gain_stddev_at_cost(runs, cost) for cost in get_max_cost_range(runs,increment) ] )

def get_avg_derived_gain_plusSD_at_cost_range( gainId, runs, increment, factor = 1.0 ):
    return calc_and_get_by_fname( [ gainId, id(runs), increment, factor ],
                         lambda : [ get_average_derived_gain_at_cost(gainId, runs, cost) + \
                                   factor * get_derived_gain_stddev_at_cost(gainId, runs, cost) for cost in get_max_cost_range(runs,increment) ] )

def get_cumulated_cost_stddevs_at_total_rank_range( runs, increment = 1 ):
    return calc_and_get_by_fname( [ id(runs), increment ],
                         lambda : [ get_cumulated_cost_stddev_at_rank(runs, rank) for rank in get_max_rank_range(runs,increment) ] )

def get_avg_cumulated_cost_plusSD_at_total_rank_range( runs, increment = 1, factor = 1.0 ):
    return calc_and_get_by_fname( [ id(runs), increment, factor ],
                         lambda : [ get_average_cumulated_cost_at_total_rank(runs, rank) + \
                                   factor * get_cumulated_cost_stddev_at_rank(runs, rank) for rank in get_max_rank_range(runs,increment) ] )

def get_average_cumulated_gains_at_total_rank_range( runs, increment = 1 ):
    return calc_and_get( 'avgGainsAtRankRanges', [ id(runs), increment ],
                         lambda : [ get_average_cumulated_gain_at_total_rank(runs, rank) for rank in get_max_rank_range(runs,increment) ] )

def get_average_cross_session_cumulated_gains_at_total_rank_range( sessions, increment = 1 ):
    return calc_and_get_by_fname( [ id(sessions), increment ],
                         lambda : get_averaged_list_of_values( [ get_average_cumulated_gains_at_total_rank_range(runs, increment) for runs in sessions ] ) )

def get_average_derived_gains_at_total_rank_range( gainId, runs, increment = 1 ):
    return calc_and_get_by_fname( [ id(runs), increment, gainId ],
                         lambda : [ get_average_derived_gain_at_total_rank(gainId, runs, rank ) for rank in get_max_rank_range(runs,increment) ] )

def get_average_top_cumulated_gains_at_total_rank_range( runs, increment = 1, proportion = 25, bottom = False ):
    return calc_and_get_by_fname( [ id(runs), increment, proportion, bottom ],
                         lambda : [ get_average_top_cumulated_gain_at_total_rank(runs, rank, proportion, bottom) for rank in get_max_rank_range(runs,increment) ] )

def get_average_top_derived_gains_at_total_rank_range( runs, gainId, increment = 1, proportion = 25, bottom = False ):
    return calc_and_get_by_fname( [ gainId, id(runs), increment, proportion, bottom ],
                         lambda : [ get_average_top_derived_gain_at_total_rank(gainId, runs, rank, proportion, bottom) for rank in get_max_rank_range(runs,increment) ] )

def get_max_cumulated_gains_at_total_rank_range( runs, increment = 1 ):
    return calc_and_get( 'maxGainsAtRankRanges', [ id(runs), increment ],
                         lambda : [ get_max_cumulated_gain_at_total_rank(runs, rank) for rank in get_max_rank_range(runs,increment) ] )

def get_min_cumulated_gains_at_total_rank_range( runs, increment = 1 ):
    return calc_and_get( 'minGainsAtRankRanges', [ id(runs), increment ],
                         lambda : [ get_min_cumulated_gain_at_total_rank(runs, rank) for rank in get_max_rank_range(runs, increment) ] )

def get_amount_of_runs_at_total_rank_range( runs, increment = 1 ):
    return calc_and_get( 'amtRunsAtRankRanges', [ id(runs), increment ],
                         lambda : [ get_amount_of_runs_at_total_rank(runs, rank) for rank in get_max_rank_range(runs, increment) ] )

def get_average_amount_of_runs_at_total_rank_range( sessions, increment = 1 ):
    return calc_and_get_by_fname( [ id(sessions), increment ],
                         lambda : get_averaged_list_of_values( [ get_amount_of_runs_at_total_rank_range(runs, increment) for runs in sessions ] ) )

def get_average_cumulated_gains_at_cost_range( runs, increment ):
    return calc_and_get( 'avgGainsAtCostRanges', [ id(runs), increment ],
                         lambda : [ get_average_cumulated_gain_at_cost(runs, cost) for cost in get_max_cost_range(runs,increment) ] )

def get_average_cross_session_cumulated_gains_at_cost_range( sessions, increment ):
    return calc_and_get_by_fname( [ id(sessions), increment ],
                         lambda : get_averaged_list_of_values( [ get_average_cumulated_gains_at_cost_range(runs, increment) for runs in sessions ] ) )

def get_average_derived_gains_at_cost_range( gainId, runs, increment ):
    return calc_and_get_by_fname( [ gainId, id(runs), increment ],
                         lambda : [ get_average_derived_gain_at_cost(gainId, runs, cost) for cost in get_max_cost_range(runs,increment) ] )

def get_average_top_cumulated_gains_at_cost_range( runs, increment, proportion = 25, bottom = False ):
    return calc_and_get_by_fname( [ id(runs), increment, proportion, bottom ],
                         lambda : [ get_average_top_cumulated_gain_at_cost(runs, cost, proportion, bottom) for cost in get_max_cost_range(runs,increment) ] )

def get_average_top_derived_gains_at_cost_range( runs, gainId, increment, proportion = 25, bottom = False ):
    return calc_and_get_by_fname( [ gainId, id(runs), increment, proportion, bottom ],
                         lambda : [ get_average_top_derived_gain_at_cost(gainId, runs, cost, proportion, bottom) for cost in get_max_cost_range(runs,increment) ] )

def get_max_cumulated_gains_at_cost_range( runs, increment ):
    return calc_and_get( 'maxGainsAtCostRanges', [ id(runs), increment ],
                         lambda : [ get_max_cumulated_gain_at_cost(runs, cost) for cost in get_max_cost_range(runs,increment) ] )

def get_min_cumulated_gains_at_cost_range( runs, increment ):
    return calc_and_get( 'minGainsAtCostRanges', [ id(runs), increment ],
                         lambda : [ get_min_cumulated_gain_at_cost(runs, cost) for cost in get_max_cost_range(runs,increment) ] )

def get_amount_of_runs_at_cost_range( runs, increment ):
    return calc_and_get( 'amtRunsAtCostRanges', [ id(runs), increment ],
                         lambda : [ get_amount_of_runs_at_cost(runs, cost) for cost in get_max_cost_range(runs,increment) ] )

def get_average_amount_of_runs_at_cost_range( sessions, increment ):
    return calc_and_get_by_fname( [ id(sessions), increment ],
                         lambda : get_averaged_list_of_values( [ get_amount_of_runs_at_cost_range(runs, increment) for runs in sessions ] ) )

def get_average_cumulated_costs_at_total_rank_range( runs, increment = 1 ):
    return calc_and_get( 'avgCostsAtRankRanges', [ id(runs), increment ],
                         lambda : [ get_average_cumulated_cost_at_total_rank(runs, rank) for rank in get_max_rank_range(runs,increment) ] )

def get_average_cross_session_cumulated_costs_at_total_rank_range( sessions, increment = 1 ):
    return calc_and_get_by_fname( [ id(sessions), increment ],
                         lambda : get_averaged_list_of_values( [ get_average_cumulated_costs_at_total_rank_range(runs, increment) for runs in sessions ] ) )

def get_average_top_cumulated_costs_at_total_rank_range( runs, increment = 1, proportion = 25, bottom = False ):
    return calc_and_get_by_fname( [ id(runs), increment, proportion, bottom ],
                         lambda : [ get_average_top_cumulated_cost_at_total_rank(runs, rank, proportion, bottom) for rank in get_max_rank_range(runs,increment) ] )

def get_max_cumulated_costs_at_total_rank_range( runs, increment = 1 ):
    return calc_and_get( 'maxCostsAtRankRanges', [ id(runs), increment ],
                         lambda : [ get_max_cumulated_cost_at_total_rank(runs, rank) for rank in get_max_rank_range(runs,increment) ] )

def get_min_cumulated_costs_at_total_rank_range( runs, increment = 1 ):
    return calc_and_get( 'minCostsAtRankRanges', [ id(runs), increment ],
                         lambda : [ get_min_cumulated_cost_at_total_rank(runs, rank) for rank in get_max_rank_range(runs,increment) ] )

def get_max_cumulated_gain_at_total_rank( runs, rank ):
    def getMaxGain():
        gains,amtNones = get_gains_at_total_rank(runs,rank)
        return max( gains )
    return calc_and_get_by_fname( [ id(runs), rank ], getMaxGain )

def get_min_cumulated_gain_at_total_rank( runs, rank ):
    def getMinGain():
        gains,amtNones = get_gains_at_total_rank(runs,rank)
        return min( gains )
    return calc_and_get_by_fname( [ id(runs), rank ], getMinGain )

def get_amount_of_runs_at_total_rank( runs, rank ):
    def getAmtRuns():
        gains,amtNones = get_gains_at_total_rank(runs,rank)
        return len(runs) - amtNones
    return calc_and_get_by_fname( [ id(runs), rank ], getAmtRuns )

def get_cumulated_gain_stddev_at_rank( runs, rank ):
    def get_stddev():
        gainSq = 0
        amtNones = 0
        amtRuns = len( runs )
        for run in runs:
            state = run.get_last_state_at_total_rank( rank )
            if state != None:
                gainSq += state.cumulatedGain**2
            else:
                amtNones += 1
        avgOfSqGains = float(gainSq)/float(amtRuns - amtNones)
        sqOfAvgGain = get_average_cumulated_gain_at_total_rank( runs, rank )**2
        try:
            return math.sqrt( avgOfSqGains - sqOfAvgGain )
        except ValueError:
            return 0.0 # Rounding errors cause variance to be negative in rare cases
    return calc_and_get_by_fname( [ id(runs), rank ], get_stddev )

def get_derived_gain_stddev_at_rank( gainId, runs, rank ):
    def get_stddev():
        gainSq = 0
        amtNones = 0
        amtRuns = len( runs )
        for run in runs:
            state = run.get_last_state_at_total_rank( rank )
            if state != None:
                gainSq += state.gains[ gainId ]**2
            else:
                amtNones += 1
        avgOfSqGains = float(gainSq)/float(amtRuns - amtNones)
        sqOfAvgGain = get_average_derived_gain_at_total_rank( gainId, runs, rank )**2
        try:
            return math.sqrt( avgOfSqGains - sqOfAvgGain )
        except ValueError:
            return 0.0 # Rounding errors cause variance to be negative in rare cases
    return calc_and_get_by_fname( [ gainId, id(runs), rank ], get_stddev )

def get_cumulated_gain_stddev_at_cost( runs, cost ):
    def get_stddev():
        gainSq = 0
        amtNones = 0
        amtRuns = len( runs )
        for run in runs:
            state = run.get_first_state_at_cost( cost )
            if state != None:
                gainSq += state.cumulatedGain**2
            else:
                amtNones += 1
        avgOfSqGains = float(gainSq)/float(amtRuns - amtNones)
        sqOfAvgGain = get_average_cumulated_gain_at_cost( runs, cost )**2
        try:
            return math.sqrt( avgOfSqGains - sqOfAvgGain )
        except ValueError:
            return 0.0 # Rounding errors cause variance to be negative in rare cases
    return calc_and_get_by_fname( [ id(runs), cost ], get_stddev )

def get_derived_gain_stddev_at_cost( gainId, runs, cost ):
    def get_stddev():
        gainSq = 0
        amtNones = 0
        amtRuns = len( runs )
        for run in runs:
            state = run.get_first_state_at_cost( cost )
            if state != None:
                gainSq += state.gains[ gainId ]**2
            else:
                amtNones += 1
        avgOfSqGains = float(gainSq)/float(amtRuns - amtNones)
        sqOfAvgGain = get_average_derived_gain_at_cost( gainId, runs, cost )**2
        try:
            return math.sqrt( avgOfSqGains - sqOfAvgGain )
        except ValueError:
            return 0.0 # Rounding errors cause variance to be negative in rare cases
    return calc_and_get_by_fname( [ gainId, id(runs), cost ], get_stddev )

def get_cumulated_cost_stddev_at_rank( runs, rank ):
    def get_stddev():
        costSq = 0
        amtNones = 0
        amtRuns = len( runs )
        for run in runs:
            state = run.get_last_state_at_total_rank( rank )
            if state != None:
                costSq += state.cumulatedCost**2
            else:
                amtNones += 1
        avgOfSqCosts = float(costSq)/float(amtRuns - amtNones)
        sqOfAvgCost = get_average_cumulated_cost_at_total_rank( runs, rank )**2
        try:
            return math.sqrt( avgOfSqCosts - sqOfAvgCost )
        except ValueError:
            return 0.0 # Rounding errors cause variance to be negative in rare cases
    return calc_and_get_by_fname( [ id(runs), rank ], get_stddev )

def get_average_cumulated_cost_at_total_rank( runs, rank ):
    def getAvgCost():
        costs,amtNones = get_costs_at_total_rank(runs,rank)
        amtRuns = len(runs)
        return sum( costs )/float(amtRuns - amtNones)
    return calc_and_get_by_fname( [ id(runs), rank ], getAvgCost )

def get_average_top_cumulated_cost_at_total_rank( runs, rank, proportion = 25, bottom = False ):
    def getAvgCost():
        costs = get_top_costs_at_total_rank(runs,rank, proportion, bottom)
        return sum( costs )/float(len(costs))
    return calc_and_get_by_fname( [ id(runs), rank, proportion, bottom ], getAvgCost )

def get_max_cumulated_cost_at_total_rank( runs, rank ):
    def getMaxCost():
        costs,amtNones = get_costs_at_total_rank(runs,rank)
        return max( costs )
    return calc_and_get_by_fname( [ id(runs), rank ], getMaxCost )

def get_min_cumulated_cost_at_total_rank( runs, rank ):
    def getMinCost():
        costs,amtNones = get_costs_at_total_rank(runs,rank)
        return min( costs )
    return calc_and_get_by_fname( [ id(runs), rank ], getMinCost )

def get_average_cumulated_gain_at_cost( runs, cost ):
    def get_avg_gain():
        gains,amtNones = get_gains_at_cost(runs,cost)
        amtRuns = len( runs )
        return float(sum( gains ))/float(amtRuns - amtNones)
    return calc_and_get_by_fname( [ id(runs), cost ], get_avg_gain )

def get_average_derived_gain_at_cost( gainId, runs, cost ):
    def get_avg_gain():
        gains = get_derived_gains_at_cost(gainId,runs,cost)
        amtRuns = len( runs )
        return float(sum( gains ))/float(len(gains))
    return calc_and_get_by_fname( [ gainId, id(runs), cost ], get_avg_gain )

def get_average_top_cumulated_gain_at_cost( runs, cost, proportion = 25, bottom = False ):
    def get_avg_gain():
        gains = get_top_gains_at_cost(runs, cost, proportion, bottom)
        return float(sum( gains ))/float(len(gains))
    return calc_and_get_by_fname( [ id(runs), cost, proportion, bottom ], get_avg_gain )

def get_average_top_derived_gain_at_cost( gainId, runs, cost, proportion = 25, bottom = False ):
    def get_avg_gain():
        gains = get_top_derived_gains_at_cost(gainId, runs, cost, proportion, bottom)
        return float(sum( gains ))/float(len(gains))
    return calc_and_get_by_fname( [ gainId, id(runs), cost, proportion, bottom ], get_avg_gain )

def get_max_cumulated_gain_at_cost( runs, cost ):
    def get_max_gain():
        gains,amtNones = get_gains_at_cost(runs,cost)
        return max( gains )
    return calc_and_get_by_fname( [ id(runs), cost ], get_max_gain )

def get_min_cumulated_gain_at_cost( runs, cost ):
    def get_min_gain():
        gains,amtNones = get_gains_at_cost(runs,cost)
        return min( gains )
    return calc_and_get_by_fname( [ id(runs), cost ], get_min_gain )

def get_amount_of_runs_at_cost( runs, cost ):
    def get_amt_runs():
        gains,amtNones = get_gains_at_cost(runs,cost)
        amtRuns = len( runs )
        return amtRuns - amtNones
    return calc_and_get_by_fname( [ id(runs), cost ], get_amt_runs )

def get_average_cumulated_cost( runs ):
    return calc_and_get_by_fname( [ id(runs) ],
                                  lambda : sum( get_final_costs(runs) )/float(len(runs)) )

def get_max_cumulated_gain( runs ):
    return calc_and_get_by_fname( [ id(runs) ],
                                  lambda : max( get_final_gains(runs) ) )

def get_max_total_rank( runs ):
    return calc_and_get_by_fname( [ id(runs) ],
                                  lambda : max( get_final_total_ranks(runs) ) )

def get_max_cross_session_total_rank( sessions ):
    return calc_and_get_by_fname( [ id(sessions) ],
                                  lambda : max( get_final_cross_session_total_ranks(sessions) ) )

def get_max_cumulated_cost( runs ):
    return calc_and_get_by_fname( [ id(runs) ],
                                  lambda : max( get_final_costs(runs) ) )

def get_min_cumulated_gain( runs ):
    return calc_and_get_by_fname( [ id(runs) ],
                                  lambda : min( get_final_gains(runs) ) )

def get_min_cumulated_cost( runs ):
    return calc_and_get_by_fname( [ id(runs) ],
                                  lambda : min( get_final_costs(runs) ) )

def get_min_cross_session_cumulated_cost( sessions ):
    return calc_and_get_by_fname( [ id(sessions) ],
                                  lambda : min( [ get_min_cumulated_cost(runs) for runs in sessions ] ) )

def get_min_total_rank( runs ):
    return calc_and_get_by_fname( [ id(runs) ],
                                  lambda : min( get_final_total_ranks(runs) ) )

def get_total_rank_variance( runs ):
    return sum( [ float(run.history[ -1 ].totalRank**2) for run in runs ] )/float(len(runs)) \
        - get_average_total_rank(runs)**2

def get_cumulated_gain_variance( runs ):
    return sum( [ float(run.history[ -1 ].cumulatedGain**2) for run in runs ] )/float(len(runs)) \
        - get_average_cumulated_gain(runs)**2

def get_cumulated_cost_variance( runs ):
    return sum( [ float(run.history[ -1 ].cumulatedCost**2) for run in runs ] )/float(len(runs)) \
        - get_average_cumulated_cost(runs)**2

def get_averaged_list_of_values( list_of_lists ):
    return [sum(n)/len(n) for n in zip(*list_of_lists)]

def get_callback_interface():
    return {
            # CG
            'average_cumulated_gain': {
                'rank': get_average_top_cumulated_gains_at_total_rank_range,
                'cost': get_average_top_cumulated_gains_at_cost_range,
            },

            'average_cumulated_gain_SD': {
                'rank': get_avg_cumulated_gain_plusSD_at_total_rank_range,
                'cost': get_avg_cumulated_gain_plusSD_at_cost_range
            },

            'average_derived_gain': {
                'rank': get_average_top_derived_gains_at_total_rank_range,
                'cost': get_average_top_derived_gains_at_cost_range
            },

            'average_derived_gain_SD': {
                'rank': get_avg_derived_gain_plusSD_at_total_rank_range,
                'cost': get_avg_derived_gain_plusSD_at_cost_range
            },

            'average_cost': {
                'rank': get_average_top_cumulated_costs_at_total_rank_range
            },

            'average_cost_SD': {
                'rank': get_avg_cumulated_cost_plusSD_at_total_rank_range
            }
        }

def get_range_callback_interface():
    return {
            'rank': {
                     'max_range': get_max_rank_range,
                     'min_range': get_min_rank_range,
                     'amt_runs': get_amount_of_runs_at_total_rank_range
                     },
            'cost': {
                     'max_range': get_max_cost_range,
                     'min_range': get_min_cost_range,
                     'amt_runs': get_amount_of_runs_at_cost_range
                     }
            }

