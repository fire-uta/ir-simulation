# -*- coding: latin-1 -*-
'''
Created on 6.11.2012

@author: Teemu Pääkkönen
'''

import sys
import random
from qsdl.simulator.errors.IrsimError import IrsimError
import qsdl.parser.qsdl01 as qsdl
import qsdl.parser.parsedQSDL as parsedQSDL
from qsdl.parser.parsedQSDL import SimDescriptor
from qsdl.simulator.simulation import Simulation
from qsdl.simulator.events import TransitionConsiderBegin
from qsdl.simulator.events import ProbabilityCalculated
from qsdl.simulator.events import DocumentChanged
from qsdl.simulator.observers import TransitionConsiderationRecorder
from qsdl.simulator.observers import ProbabilityRecorder
from qsdl.simulator.observers import DocumentIdRecorder


def register_observers(simulation):
    simulation.registerObserver( TransitionConsiderBegin, TransitionConsiderationRecorder() )
    simulation.registerObserver( ProbabilityCalculated, ProbabilityRecorder() )
    simulation.registerObserver( DocumentChanged, DocumentIdRecorder() )


def run_sessions(config, runId):
    # initiate random seed for the simulation
    seed = config.get_random_seed()
    random.seed( seed )

    parsedQSDL.set_variable_callback_arguments(config.get_variable_callback_arguments(runId))
    simDesc = SimDescriptor( qsdl.CreateFromDocument( config.get_simulation_file().read() ), config )
    sessionIdIterator = config.get_session_id_iterator()
    v_print = config.get_verbose_writer()
    sessions = []
    for sessionId in sessionIdIterator:
        simulationIterations = []
        for iteration in range( config.get_iterations( sessionId ) ):
            reader = config.get_reader( sessionId )
            simulationIteration = Simulation(simDesc, config, reader, iteration, runId)

            register_observers(simulationIteration)

            while True:
                v_print( lambda : 'Gain: %g - Cost: %g - Total rank: %g - '
                    'Query rank: %g - Query: %g' % (
                        simulationIteration.currentState.cumulatedGain,
                        simulationIteration.currentState.cumulatedCost,
                        simulationIteration.currentState.totalRank,
                        simulationIteration.currentState.currentQueryRank,
                        simulationIteration.currentState.queryIndex + 1) )

                '''
                uinput = raw_input('Press return to advance, enter Q to quit.')
                if uinput.lower() == 'q':
                    break
                '''

                try:
                    notFinal = simulationIteration.advance()
                except IrsimError as ie:
                    print >> sys.stderr, 'ERROR:', ie.value
                    sys.exit()

                if not notFinal:
                    v_print( lambda : 'Final action reached!' )
                    break

                v_print( lambda : 'Ran action: %s' % simulationIteration.history[ len(simulationIteration.history) - 1 ].nextTransition.target )

            simulationIterations.append( simulationIteration )
        sessions.append( simulationIterations )

    return sessions
