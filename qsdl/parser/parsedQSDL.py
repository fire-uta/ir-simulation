# -*- coding: latin-1 -*-
'''
Created on 26.9.2012

@author: Teemu Pääkkönen
'''
from qsdl.simulator.errors.TransitionError import TransitionError
from qsdl.simulator.errors.ConfigurationMissingError import ConfigurationMissingError
from qsdl.simulator.errors.CallbackError import CallbackError

def pack_callback_arguments( callback ):
    '''
    Helper function for packing callback arguments into a dict.
    The dict can then be unpacked when calling the callbacks.
    '''
    argDict = {}
    for arg in callback.argument:
        argDict[ arg.name ] = arg.value_
    return argDict

class SimDescriptor(object):
    '''
    a QSDL object with key-keyrefs resolved into relationships
    Members:
    doc <- reference to the original parsed XML document object
    actions <- dictionary of actions
    probabilities <- dictionary of probabilities
    conditions <- dictionary of conditions
    '''


    def __init__(self, pyxbQSDLDoc, config):

        self.doc = pyxbQSDLDoc
        self.config = config

        self.actions = dict( [ [ action.id, action ] for action in pyxbQSDLDoc.actions.action ] )
        self.probabilities = dict( [ [ probability.id, probability ] for probability \
                                    in pyxbQSDLDoc.probabilities.probability ] )
        self.conditions = dict( [ [ condition.id, condition ] for condition \
                                    in pyxbQSDLDoc.probability_conditions.probability_condition ] )
        self.costs = dict( [ [ cost.id, cost ] for cost in pyxbQSDLDoc.costs.cost ] )
        self.gains = dict( [ [ gain.id, gain ] for gain in pyxbQSDLDoc.gains.gain ] )
        self.decays = dict( [ [ decay.id, decay ] for decay in pyxbQSDLDoc.decays.decay ] )
        self.transitionSources = dict( [ [ source.source, source ] for source \
                                      in pyxbQSDLDoc.transitions.from_ ] )

        self.initialActionId = pyxbQSDLDoc.actions.initial
        self.initialAction = self.actions[ self.initialActionId ]

        for source in self.transitionSources.itervalues():
            source.negDecayDivider = sum( [ 1.0 if to.decay_effect == "-" else 0.0 for to in source.to] )
            source.posDecayDivider = sum( [ 1.0 if to.decay_effect == "+" else 0.0 for to in source.to] )
            source.decayDefinition = None if source.decay == None \
                            else self.get_decay_by_id( source.decay )
            source.decayFunction = None if source.decayDefinition == None \
                            else self.get_decay_function_by_name( source.decayDefinition.callback.name )
            source.targets = []
            for target in source.to:
                # Create a simple list for performance reasons
                source.targets.append( target )

                # Bind source and target since we are creating lambdas inside a loop
                def setDecayFunction( trgt_, src_ ):
                    # Pre-calc decay function
                    decayF = lambda decayFunc, sim : 0.0
                    if src_.decayDefinition != None:
                        callbackArgs = pack_callback_arguments(src_.decayDefinition.callback)
                        if trgt_.decay_effect == '-':
                            decayF = lambda decayFunc, sim : (-1.0 * decayFunc( sim, **callbackArgs ))/src_.negDecayDivider
                        elif trgt_.decay_effect == '+':
                            decayF = lambda decayFunc, sim : decayFunc( sim, **callbackArgs )/src_.posDecayDivider
                    trgt_.decayFunction = decayF

                setDecayFunction( target, source )

        # Pack callback args on init for performance reasons
        for condition in self.conditions.itervalues():
            condition.callbackArgs = pack_callback_arguments( condition.callback )
        for gain in self.gains.itervalues():
            if gain.callback:
                gain.callbackArgs = pack_callback_arguments( gain.callback )
        for cost in self.costs.itervalues():
            if cost.callback:
                cost.callbackArgs = pack_callback_arguments( cost.callback )

        def createCallbackLambda( ifStatement ):
            neg = ifStatement.negation
            cbArgs = ifStatement.conditionRef.callbackArgs
            ifStatement.conditionCallbackLambda = \
                lambda sim : ifStatement.conditionCallback( sim, neg, **cbArgs )

        # Generate a conditions list for probabilities
        for probability in self.probabilities.itervalues():
            probability.conditions = []
            if probability.if_:
                probability.conditions.append( probability.if_ )
                probability.if_.conditionRef = self.get_condition_by_id( probability.if_.condition )
                probability.if_.conditionCallback = \
                    config.get_condition_callbacks()[ probability.if_.conditionRef.callback.name ]
                createCallbackLambda( probability.if_ )
                for elseif in probability.else_if:
                    probability.conditions.append( elseif )
                    elseif.conditionRef = self.get_condition_by_id( elseif.condition )
                    elseif.conditionCallback = config.get_condition_callbacks()[ elseif.conditionRef.callback.name ]
                    createCallbackLambda( elseif )

    def get_action_by_id(self, id_):
        return self.actions[ id_ ]

    def get_condition_by_id(self, id_):
        return self.conditions[ id_ ]

    def get_transition_source_for_action_id(self, id_ ):
        try:
            return self.transitionSources[ id_ ]
        except KeyError:
            raise TransitionError( 'No transitions defined from action id \'%s\'. Please check simulation description.' % id_ )

    def get_probability_for_probability_id(self, id_):
        return self.probabilities[ id_ ]

    def get_decay_by_id(self, id_):
        try:
            return self.decays[ id_ ]
        except KeyError:
            raise ConfigurationMissingError( 'Decay definition for id \'%s\' not found. Check configuration. Available definitions: %s' % (id_, repr(self.decays.keys())) )

    def get_cost_callback_by_id(self, id_):
        try:
            return self.costs[ id_ ]
        except KeyError:
            raise ConfigurationMissingError( 'Cost definition for id \'%s\' not found. Check configuration. Available definitions: %s' % (id_, repr(self.costs.keys())) )

    def get_gain_callback_by_id(self, id_):
        try:
            return self.gains[ id_ ]
        except KeyError:
            raise ConfigurationMissingError( 'Gain definition for id \'%s\' not found. Check configuration. Available definitions: %s' % (id_, repr(self.gains.keys())) )

    def get_decay_function_by_name(self, name):
        try:
            return self.config.get_decays()[ name ]
        except KeyError:
            raise CallbackError(
                'Decay callback \'%s\' not found. Check callback mapping. Available callbacks: %s' \
                % ( name, repr(self.config.get_decays().keys())))

