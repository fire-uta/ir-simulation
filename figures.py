# -*- coding: latin-1 -*-
'''
Created on 6.12.2012

@author: Teemu Pääkkönen
'''

import stats
import matplotlib.pyplot as pyplot
import qsdl.parser.parsedQSDL as parsedQSDL
from matplotlib.figure import SubplotParams
from matplotlib.font_manager import FontProperties
from itertools import cycle


class FiguresConfig:
    pass

FiguresConfig.runId = None
FiguresConfig.outputDirectory = None


def setup_colors():
    pyplot.rc('axes', color_cycle=['#ff0000','#00ff00','#0000ff',
        '#ffff00','#ff00ff','#00ffff',
        '#000000','#ff8000','#0080ff',
        '#ff0080','#80ff00','#8000ff',
        '#00ff80','#ff8080','#80ff80',
        '#8080ff'])


setup_colors()

def set_run_id(runId):
    FiguresConfig.runId = runId


def set_output_directory(directory):
    FiguresConfig.outputDirectory = directory


def get_filename_prefix():
    if FiguresConfig.runId is None:
        raise RuntimeError("Run id not set")
    return FiguresConfig.runId + '-'


def get_filename(type, runs, format='png'):
    session_id = get_session_id(runs)
    return FiguresConfig.outputDirectory + '/' + get_filename_prefix() + type + '-' + session_id + '.' + format

def get_session_id( runs ):
    return str(runs[0].get_session_id())

def pack_callback_arguments( callback ):
    return parsedQSDL.pack_callback_arguments( callback )

def get_plot_font():
    fontProp = FontProperties()
    fontProp.set_size('small')
    return fontProp

def get_markers_cycler():
    markers = ['o','v','s','*','^','p','x','D','h','+']
    return cycle(markers)

def add_values_plot( figure, xLabel, yLabel, xRange, yValueLists ):
    markers_cycler = get_markers_cycler()
    plt = figure.add_subplot(211, xlabel=xLabel, ylabel=yLabel)
    plt.grid(color='#666666', linestyle=':', linewidth=0.5)
    for (label,yValues) in yValueLists:
        plt.plot( xRange[:len(yValues)], yValues, label=label, marker=next(markers_cycler) )
    return plt

def add_runs_plot( figure, sharedXPlot, xRange, runValues ):
    plt = figure.add_subplot(212, sharex=sharedXPlot, ylabel='runs')
    plt.grid(color='#666666', linestyle=':', linewidth=0.5)
    plt.plot( xRange[:len(runValues)], runValues, label='nRuns' )
    return plt

def add_values_legend( valuesPlot ):
    return valuesPlot.legend( loc='center left', bbox_to_anchor=(1,0.5),
        prop=get_plot_font(), fancybox=True, shadow=True, ncol=1 )

def defaultPlot( xlabel, ylabel, xRange, yValueLists, runValues, figFileName ):
    fig = pyplot.figure( figsize=(12, 10), dpi=100, subplotpars=SubplotParams(right=0.8) )
    valuesPlot = add_values_plot( fig, xlabel, ylabel, xRange, yValueLists )
    valuesLegend = add_values_legend( valuesPlot )
    add_runs_plot( fig, valuesPlot, xRange, runValues )
    fig.savefig( figFileName, bbox_extra_artists=(valuesLegend,), bbox_inches='tight' )
    pyplot.close( fig )

def plotAverageGainsAtRankAcrossSessions( sessions ):
    yValueLists = []
    max_rank_range = None
    runAmounts = []
    for simulationIterations in sessions:
        sessid = get_session_id(simulationIterations)
        yValueLists.append( (sessid, stats.get_average_cumulated_gains_at_total_rank_range( simulationIterations )))
        max_rank_range = max( max_rank_range, stats.get_max_rank_range( simulationIterations ) )
        runAmounts.append( stats.get_amount_of_runs_at_total_rank_range( simulationIterations ) )

    yValueLists.append( ('avg', stats.get_averaged_list_of_values( zip(*yValueLists)[1] ) ) ) # Get average of averages
    defaultPlot( 'rank', 'avg cg', max_rank_range, yValueLists,
        stats.get_averaged_list_of_values( runAmounts ),
        get_filename_prefix() + 'X-session-gainAtRank.png')


def plotAverageGainsAtCostAcrossSessions( sessions, costIncrement ):
    yValueLists = []
    max_cost_range = None
    runAmounts = []
    for simulationIterations in sessions:
        sessid = get_session_id(simulationIterations)
        yValueLists.append( (sessid,
            stats.get_average_cumulated_gains_at_cost_range(
                simulationIterations, costIncrement )))
        max_cost_range = max( max_cost_range,
            stats.get_max_cost_range( simulationIterations, costIncrement ) )
        runAmounts.append( stats.get_amount_of_runs_at_cost_range(
            simulationIterations, costIncrement ) )

    yValueLists.append( ('avg', stats.get_averaged_list_of_values( zip(*yValueLists)[1] ) ) ) # Get average of averages
    defaultPlot( 'cost', 'avg cg', max_cost_range, yValueLists,
        stats.get_averaged_list_of_values( runAmounts ),
        get_filename_prefix() + 'X-session-gainAtCost.png')


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
                 stats.get_amount_of_runs_at_total_rank_range(runs), get_filename('gainAtRank', runs))

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
                 stats.get_amount_of_runs_at_cost_range(runs, costIncrement), get_filename('gainAtCost', runs))

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
                 stats.get_amount_of_runs_at_total_rank_range(runs), get_filename(gainId + 'AtRank', runs))

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
        ('avg +1SD', stats.get_avg_cumulated_cost_plusSD_at_total_rank_range( runs, increment = 1, factor = 1 ) ),
        ('avg -1SD', stats.get_avg_cumulated_cost_plusSD_at_total_rank_range( runs, increment = 1, factor = -1 ) )
                   ]
    defaultPlot( 'rank', 'cost', stats.get_max_rank_range( runs ), yValueLists,
                 stats.get_amount_of_runs_at_total_rank_range(runs), get_filename('costAtRank', runs))

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

        defaultPlot( range_, yAxis.label, rangeRange, yValueLists, amtRuns, get_filename(figure.id, runs))

