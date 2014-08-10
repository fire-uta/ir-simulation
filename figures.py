# -*- coding: latin-1 -*-
'''
Created on 6.12.2012

@author: Teemu P��kk�nen
'''

import stats
import matplotlib.pyplot as pyplot
import qsdl.parser.parsedQSDL as parsedQSDL
from matplotlib.figure import SubplotParams

def pack_callback_arguments( callback ):
    return parsedQSDL.pack_callback_arguments( callback )

def defaultPlot( xlabel, ylabel, xRange, yValueLists, runValues, figFileName ):
    fig = pyplot.figure( figsize=(12, 10), dpi=100, subplotpars=SubplotParams(right=0.8) )
    plt = fig.add_subplot(211, xlabel=xlabel, ylabel=ylabel)
    for (label,yValues) in yValueLists:
        plt.plot( xRange, yValues, label=label )
    plt.legend( loc=(1.05,0) )
    plt2 = fig.add_subplot(212, sharex=plt, ylabel='runs')
    plt2.plot( xRange, runValues, label='nRuns' )
    fig.savefig( figFileName )
    
def plotGainsAtRank( runs ):
    sessid = str(runs[0].get_session_id())
    yValueLists = [
        ('avg', stats.get_average_cumulated_gains_at_total_rank_range( runs ) ),
        ('top50%', stats.get_average_top_cumulated_gains_at_total_rank_range( runs, proportion = 50 ) ),
        ('bottom50%', stats.get_average_top_cumulated_gains_at_total_rank_range( runs, proportion = 50, bottom = True ) ),
        ('avg +1SD', stats.get_avg_cumulated_gain_plusSD_at_total_rank_range( runs ) ),
        ('avg -1SD', stats.get_avg_cumulated_gain_plusSD_at_total_rank_range( runs, -1 ) )
                   ]
    defaultPlot( 'rank', 'cg', stats.get_max_rank_range( runs ), yValueLists,
                 stats.get_amount_of_runs_at_total_rank_range(runs), 'gainAtRank-' + sessid + '.png' )

def plotGainsAtCost( runs, costIncrement ):
    sessid = str(runs[0].get_session_id())
    yValueLists = [
        ('avg', stats.get_average_cumulated_gains_at_cost_range( runs, costIncrement ) ),
        ('top50%', stats.get_average_top_cumulated_gains_at_cost_range( runs, costIncrement, proportion = 50 ) ),
        ('bottom50%', stats.get_average_top_cumulated_gains_at_cost_range( runs, costIncrement, proportion = 50, bottom = True ) ),
        ('avg +1SD', stats.get_avg_cumulated_gain_plusSD_at_cost_range( runs, costIncrement ) ),
        ('avg -1SD', stats.get_avg_cumulated_gain_plusSD_at_cost_range( runs, costIncrement, -1 ) )
                   ]
    defaultPlot( 'cost', 'cg', stats.get_max_cost_range( runs, costIncrement ), yValueLists,
                 stats.get_amount_of_runs_at_cost_range(runs, costIncrement), 'gainAtCost-' + sessid + '.png' )
    
def plotDerivedGains( runs, gainIds, costIncrement ):
    sessid = str(runs[0].get_session_id())
    for gainId in gainIds:

        yValueLists = [
            ('avg', stats.get_average_derived_gains_at_total_rank_range( gainId, runs ) ),
            ('top50%', stats.get_average_top_derived_gains_at_total_rank_range( runs, gainId, proportion = 50 ) ),
            ('bottom50%', stats.get_average_top_derived_gains_at_total_rank_range( runs, gainId, proportion = 50, bottom= True ) ),
            ('avg +1SD', stats.get_avg_derived_gain_plusSD_at_total_rank_range( gainId, runs ) ),
            ('avg -1SD', stats.get_avg_derived_gain_plusSD_at_total_rank_range( gainId, runs, -1 ) )
            ]
    
        defaultPlot( 'rank', gainId, stats.get_max_rank_range( runs ), yValueLists,
                 stats.get_amount_of_runs_at_total_rank_range(runs), gainId + 'AtRank-' + sessid + '.png' )
        
        yValueLists = [
            ('avg', stats.get_average_derived_gains_at_cost_range( gainId, runs, costIncrement ) ),
            ('top50%', stats.get_average_top_derived_gains_at_cost_range( runs, gainId, costIncrement, proportion = 50 ) ),
            ('bottom50%', stats.get_average_top_derived_gains_at_cost_range( runs, gainId, costIncrement, proportion = 50, bottom = True ) ),
            ('avg +1SD', stats.get_avg_derived_gain_plusSD_at_cost_range( gainId, runs, costIncrement ) ),
            ('avg -1SD', stats.get_avg_derived_gain_plusSD_at_cost_range( gainId, runs, costIncrement, -1 ) )
            ]
    
        defaultPlot( 'cost', gainId, stats.get_max_cost_range( runs, costIncrement ), yValueLists,
                 stats.get_amount_of_runs_at_cost_range(runs, costIncrement), 
                 gainId + 'AtCost-' + sessid + '.png' )

def plotCostsAtRank( runs ):
    sessid = str(runs[0].get_session_id())
    yValueLists = [
        ('avg', stats.get_average_cumulated_costs_at_total_rank_range( runs ) ),
        ('top50%', stats.get_average_top_cumulated_costs_at_total_rank_range( runs, proportion=50 ) ),
        ('bottom50%', stats.get_average_top_cumulated_costs_at_total_rank_range( runs, proportion=50, bottom=True ) ),
        ('avg +1SD', stats.get_avg_cumulated_cost_plusSD_at_total_rank_range( runs ) ),
        ('avg -1SD', stats.get_avg_cumulated_cost_plusSD_at_total_rank_range( runs, factor = -1 ) )
                   ]
    defaultPlot( 'rank', 'cg', stats.get_max_rank_range( runs ), yValueLists,
                 stats.get_amount_of_runs_at_total_rank_range(runs), 'costAtRank-' + sessid + '.png' )

def plotCustomFigures( runs, customFiguresDict ):
    sessid = str(runs[0].get_session_id())
    callbacks = stats.get_callback_interface()
    rangeCallbacks = stats.get_range_callback_interface()
    for figure in customFiguresDict.itervalues():
        yValueLists = []
        xAxis = figure.xaxis
        yAxis = figure.yaxis
        range_ = xAxis.range
        increment = float(xAxis.increments)
        rangeRange = rangeCallbacks[ range_ ][ 'max_range' ]( runs = runs, increment = increment )
        amtRuns = rangeCallbacks[ range_ ][ 'amt_runs' ]( runs = runs, increment = increment )
        
        for values in yAxis.values:
            callback = callbacks[ values.function ][ range_ ]
            yValueLists.append( (values.label, callback( runs = runs, increment = increment, **pack_callback_arguments(values )) ) )
        
        defaultPlot( range_, yAxis.label, rangeRange, yValueLists, amtRuns, figure.id + '-' + sessid + '.png' )
        