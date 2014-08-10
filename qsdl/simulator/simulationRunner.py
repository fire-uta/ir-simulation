# -*- coding: latin-1 -*-
'''
Created on 6.11.2012

@author: Teemu Pääkkönen
'''

import sys
import random
from qsdl.simulator.errors.IrsimError import IrsimError
import qsdl.parser.qsdl01 as qsdl
from qsdl.parser.parsedQSDL import SimDescriptor
from qsdl.simulator.simulation import Simulation
from qsdl.simulator.events import TransitionConsiderBegin
from qsdl.simulator.events import ProbabilityCalculated
from qsdl.simulator.observers import TransitionConsiderationRecorder
from qsdl.simulator.observers import ProbabilityRecorder

def register_observers( simulation ):
    simulation.registerObserver( TransitionConsiderBegin, TransitionConsiderationRecorder() )
    simulation.registerObserver( ProbabilityCalculated, ProbabilityRecorder() )

def run_sessions( config ):
    # initiate random seed for the simulation
    seed = config.get_random_seed()
    random.seed( seed )

    simDesc = SimDescriptor( qsdl.CreateFromDocument( config.get_simulation_file().read() ), config )
    sessionIdIterator = config.get_session_id_iterator()
    v_print = config.get_verbose_writer()
    sessions = []
    for sessionId in sessionIdIterator:
        runs = []
        for iteration in range( config.get_iterations( sessionId ) ):
            reader = config.get_reader( sessionId )
            simul = Simulation(simDesc, config, reader, iteration)
        
            register_observers(simul)
        
            while True:
                v_print( lambda : 'Gain: %g - Cost: %g' % (simul.currentState.cumulatedGain, simul.currentState.cumulatedCost) )
                
                '''
                uinput = raw_input('Press return to advance, enter Q to quit.')
                if uinput.lower() == 'q':
                    break
                '''
            
                try:
                    notFinal = simul.advance()
                except IrsimError as ie:
                    print >> sys.stderr, 'ERROR:', ie.value
                    sys.exit()
                
                if not notFinal:
                    v_print( lambda : 'Final action reached!' )
                    break 
            
                v_print( lambda : 'Ran action: %s' % simul.history[ len(simul.history) - 1 ].nextTransition.target )
        
            runs.append( simul )
        sessions.append( runs )
                
    return sessions
