# -*- coding: latin-1 -*-
'''
Created on 15.10.2012

@author: Teemu Pääkkönen
'''

import traceback
import callbackLoader
from qsdl.simulator import defaultTriggers
from qsdl.simulator.errors.CallbackError import CallbackError

def create_from_QSDL( qsdlTriggerDef ):

    args = {}
    for argument in qsdlTriggerDef.argument:
        args[ argument.name ] = argument.value_

    trigger = Trigger( qsdlTriggerDef.type, **args )
    return trigger

def run_triggers( qsdlAction, simulation ):
    for trigger in qsdlAction.trigger:
        runTrigger = create_from_QSDL( trigger )
        runTrigger.execute( simulation )

def get_triggers( config ):
    customTriggers = callbackLoader.get_callback_module(
                    config.get_trigger_callbacks_module_name() )
    if customTriggers != None:
        cbMap = defaultTriggers.get_callback_map().copy()
        cbMap.update( customTriggers.get_callback_map() )
        return cbMap
    return defaultTriggers.get_callback_map()

class Trigger(object):
    '''
    classdocs
    '''

    def __init__(self, tid, **kwargs):
        self.tid = tid # Trigger ID
        self.args = kwargs


    def execute(self, simulation):
        '''
        Executes the trigger. Always affects a simulation.
        '''
        try:
            get_triggers( simulation.get_config() )[ self.tid ]( simulation, **self.args )
        except KeyError as e:
            traceback.print_exc()
            raise CallbackError( 'Trigger \'%s\' not found. Check callback mapping. Available triggers: %s' % ( self.tid, repr(get_triggers( simulation.get_config() ).keys())))

