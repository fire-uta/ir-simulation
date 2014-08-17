# -*- coding: latin-1 -*-
'''
Created on 27.9.2012

@author: Teemu Pääkkönen
'''

import random
import qsdl.parser.qsdl01 as qsdl
import qsdl.simulator.triggers as triggers
import qsdl.simulator.errors.TransitionError as TransitionError
import qsdl.simulator.errors.UnknownDocumentError as UnknownDocumentError
import qsdl.parser.parsedQSDL as parsedQSDL
from qsdl.simulator.errors.CallbackError import CallbackError
from qsdl.simulator.observables import Observable
from qsdl.simulator.events import TransitionEnd
from qsdl.simulator.events import TransitionBegin
from qsdl.simulator.events import NextTransitionCalculationBegin
from qsdl.simulator.events import NextTransitionCalculationEnd
from qsdl.simulator.events import ActionBegin
from qsdl.simulator.events import ActionEnd
from qsdl.simulator.events import TransitionConsiderBegin
from qsdl.simulator.events import TransitionConsiderEnd
from qsdl.simulator.events import TransitionRejected
from qsdl.simulator.events import TransitionAccepted
from qsdl.simulator.events import ProbabilityCalculated

def generate_random_probability():
    return random.random()

def create_initial_transition( initialActionId ):
    class T: pass
    transition = T()
    transition.source = None
    transition.target = initialActionId
    transition.probability = None
    return transition

def pack_callback_arguments( callback ):
    return parsedQSDL.pack_callback_arguments( callback )


class SimulationState(object):
    '''
    objects of this class represent a simulation state
    '''
    def __init__(self, sessionId, queryIndex, totalRank, cumulatedGain,
                 cumulatedCost, nextTransition, prevAction, iteration,
                 currentQueryRank, gains):
        self.transitionsConsidered = []
        self.transitionProbabilities = {}
        self.queryIndex = queryIndex # Index of query (in query file)
        self.totalRank = totalRank # Rank within results
        self.nextTransition = nextTransition # The next transition
        self.sessionId = sessionId # ID of current strategy
        self.cumulatedGain = cumulatedGain
        self.gains = gains # User-defined gains, such as DCG, nDCG...
        self.cumulatedCost = cumulatedCost
        self.prevAction = prevAction
        self.iteration = iteration
        self.currentQueryRank = currentQueryRank
        self.ready = False # Ready to run next action?

    def add_transition_probability(self, pyxbTransition, probabilityValue):
        self.transitionProbabilities[ pyxbTransition.target ] = probabilityValue

    def add_transition_considered(self, pyxbTransition):
        self.transitionsConsidered.append( pyxbTransition.target )

    def set_ready(self):
        self.ready = True

    def get_copy(self):
        return SimulationState( self.sessionId, self.queryIndex, self.totalRank,
                                self.cumulatedGain, self.cumulatedCost, None,
                                self.nextTransition.target, self.iteration,
                                self.currentQueryRank, self.gains.copy() )

    def get_derived_gains(self):
        return self.gains

    @staticmethod
    def get_field_order( includeGains = True ):
        order = [ 'sessionId', 'iteration', 'prevAction', 'queryIndex', 'totalRank',
                'currentQueryRank', 'cumulatedGain', 'cumulatedCost', 'transitionsConsidered',
                'transitionProbabilities' ]
        if includeGains:
            order.append( 'gains' )
        return order

    def __repr__(self, *args, **kwargs):
        return repr( [self.__dict__[ field ] for field in SimulationState.get_field_order()] )

class Simulation(Observable):
    '''
    objects of this class represent a simulation (current, next and previous states)
    '''

    def __repr__(self, *args, **kwargs):
        return repr( self.history )

    def __init__(self, simDesc, config, reader, iteration, runId):

        Observable.__init__(self)

        self.simDesc = simDesc
        self.config = config
        self.reader = reader
        self.iteration = iteration
        self.runId = runId
        self.history = []
        self.seenDocuments = {}

        sessionId = reader['get_session_id']()

        self.currentState = SimulationState( sessionId, -1, 0, 0, 0,
                        create_initial_transition( simDesc.initialActionId ), None,
                        self.iteration, 0,
                        self.config.get_initial_derived_gain_values_dict( sessionId ) )
        self.currentState.set_ready()
        self.conditionCallbacks = self.config.get_condition_callbacks()
        self.v_print = self.config.get_verbose_writer()

        self.transitionStatistics = {}
        self.transitionStatistics[ 'transitionsFrom' ] = {}
        self.transitionStatistics[ 'totalsFrom' ] = {}

    def record_transition_statistics( self, fromActionId, toActionId ):
        if fromActionId == None:
            return
        if fromActionId not in self.transitionStatistics['transitionsFrom']:
            self.transitionStatistics['transitionsFrom'][ fromActionId ] = {}
            self.transitionStatistics['totalsFrom'][ fromActionId ] = 0
        if toActionId not in self.transitionStatistics['transitionsFrom'][ fromActionId ]:
            self.transitionStatistics['transitionsFrom'][ fromActionId ][ toActionId ] = 0
        self.transitionStatistics['transitionsFrom'][ fromActionId ][ toActionId ] += 1
        self.transitionStatistics['totalsFrom'][ fromActionId ] += 1


    def current_query_is_last_query(self):
        return self.currentState.queryIndex == self.reader[ 'get_amount_of_queries' ]() - 1

    def get_last_state_at_total_rank(self, rank):
        lastState = None
        for state in self.history:
            if lastState != None and lastState.totalRank == rank and state.totalRank != rank:
                return lastState
            lastState = state
        return None

    def get_first_state_at_cost(self, cost):
        lastState = None
        for state in self.history:
            if lastState != None and lastState.cumulatedCost <= cost and state.cumulatedCost >= cost:
                return state
            lastState = state
        return None

    def get_iteration(self):
        return self.iteration

    def get_config(self):
        return self.config

    def get_session_id(self):
        return self.reader[ 'get_session_id' ]()

    def get_page_size(self):
        return self.config.get_page_size( self.currentState.sessionId )

    def get_current_document_gain(self):
        return self.config.get_gain( self.currentState.sessionId, self.get_current_document_relevance_level() )

    def get_last_transition(self):
        return self.history[ -1 ].nextTransition

    def set_current_state_query_index(self, qidx):
        self.currentState.queryIndex = int(qidx)
        self.currentState.rank = 0

    def increment_current_state_rank(self):
        self.currentState.totalRank += 1
        self.currentState.currentQueryRank += 1

    def get_current_total_rank(self):
        return self.currentState.totalRank

    def get_current_query_rank(self):
        return self.currentState.currentQueryRank

    def reset_current_query_rank(self):
        self.currentState.currentQueryRank = 0

    def get_current_cumulated_cost(self):
        return self.currentState.cumulatedCost

    def increment_current_state_query_index(self):
        self.currentState.queryIndex += 1

    def get_current_query_text(self):
        return self.reader[ 'get_current_query_text' ]()

    def get_current_document_id(self):
        return self.reader[ 'get_current_document_id' ]( self.currentState.currentQueryRank )

    def get_current_document_relevance_level(self):
        return self.reader[ 'get_current_relevance_level' ]( self.get_current_document_id() )

    def get_current_results_length(self):
        return self.reader[ 'get_current_results_length' ]()

    def flag_current_document_as_seen(self):
        '''
        Flags the document as seen. The dictionary contains tuples
        (queryIndex, rank) that can be used to determine whether the document
        was seen just now or previously during this or another query.
        '''
        docid = self.get_current_document_id()
        if not self.seenDocuments.has_key( docid ):
            self.seenDocuments[ self.get_current_document_id() ] = \
                (self.currentState.queryIndex, self.currentState.totalRank)

    def current_document_has_been_seen(self):
        docid = self.get_current_document_id()
        try:
            (queryIndex, rank) = self.seenDocuments[ docid ]
            return queryIndex != self.currentState.queryIndex or rank != self.currentState.totalRank
        except:
            return False

    def calculate_derived_gains(self):
        callbackFunctionNames = self.config.get_derived_gains_callbacks_dict( self.get_session_id() )
        callbackFunctions = self.config.get_derived_gains_callbacks()
        gains = self.config.get_derived_gains_dict( self.get_session_id() )
        for gainId in self.currentState.gains.iterkeys():
            cbFunctionName = callbackFunctionNames[ gainId ]
            try:
                callback = callbackFunctions[ cbFunctionName ]
                args = pack_callback_arguments( gains[ gainId ] )
                self.currentState.gains[ gainId ] += callback( self, **args )
            except KeyError:
                raise CallbackError(
                    'Derived gain callback \'%s\' not found. Check callback mapping. Available callbacks: %s' % \
                    ( cbFunctionName, repr(callbackFunctions.keys())))

    def get_variable_probability_value(self, variableName):
        return self.config.get_variable_probability_value(self.runId, variableName)

    def get_transition_by_probability( self, valueToCheck, decay, H1, transition ):
        # FIXME: type can currently be either from qsdl xsd or config xsd
        if type( valueToCheck ) == qsdl.probability_value_direct:
            decayedValue = valueToCheck + decay

            # Notify observers that a probability value has been calculated
            self.notifyObservers( ProbabilityCalculated( self.currentState, transition, decayedValue ) )

            if decayedValue + H1.cumulatingProbability >= H1.probVal:
                self.v_print( lambda : '   %s >= remaining probability %g. Choosing action.' % (decayedValue, H1.probVal - H1.cumulatingProbability) )
                return transition
            else:
                self.v_print( lambda : '   %s < remaining probability %g. Skipping action.' % (decayedValue, H1.probVal - H1.cumulatingProbability) )
                H1.cumulatingProbability += decayedValue
                return None
        elif type( valueToCheck ) == qsdl.probability_value_variable:
            actualValue = self.get_variable_probability_value(valueToCheck)
            return self.get_transition_by_probability(actualValue, decay, H1, transition)
        else:
            self.v_print( lambda : '   Probability %s is calculated. Setting action as fallback.' % (valueToCheck) )
            H1.calculateTarget = transition
            return None

    def get_conditional_next_transition( self, ifStatement, decay, H1, transition ):
        nextTarget = None
        conditionWasMet = False
        condition = ifStatement.conditionRef
        if ifStatement.conditionCallbackLambda( self ):
            conditionWasMet = True
            nextTarget = self.get_transition_by_probability( ifStatement.value_, decay, H1, transition )
        self.v_print( lambda : '   %s Condition %s (callback %s) was %s met. Next target is %s.' % \
                              ('negation of' if ifStatement.negation else '', ifStatement.condition, condition.callback.name, '' if conditionWasMet else 'not', nextTarget) )
        return { 'conditionWasMet': conditionWasMet, 'nextTarget': nextTarget }

    def get_transition_by_probability_definition(self, probability, decay, H1, transition):
            if hasattr( probability, 'value_' ) and probability.value_ != None:
                # Direct probability value is given
                nextTarget = self.get_transition_by_probability( probability.value_, decay, H1, transition )
                if nextTarget != None:
                    return nextTarget
                else:
                    return None
            else:
                # Probability is conditional
                skipToNextTransition = False
                for condition in probability.conditions:
                    conditional = self.get_conditional_next_transition( condition, decay, H1, transition )
                    if conditional['conditionWasMet']:
                        # Condition was met. Target is none if probability check fails.
                        if conditional['nextTarget'] != None:
                            return conditional['nextTarget']
                        else:
                            skipToNextTransition = True
                            break
                    else:
                        # Skip to next condition
                        continue
                if skipToNextTransition:
                    return None

                # None of the if-else-if conditions was met. Move to the else block.
                nextTarget = self.get_transition_by_probability( probability.else_.value_, decay, H1, transition )
                if not nextTarget == None:
                    return nextTarget
                else:
                    return None


    def get_next_transition( self ):

        class H1 : pass # Helper class for containing method-local vars

        H1.probVal = generate_random_probability()
        H1.cumulatingProbability = 0.0
        H1.calculateTarget = None
        transitionSource = self.simDesc.get_transition_source_for_action_id(
                                            self.get_last_transition().target )
        decayFunction = transitionSource.decayFunction
        for transition in transitionSource.targets:

            # Notify observers of transition considering beginning
            self.notifyObservers( TransitionConsiderBegin( self.currentState, transition ) )

            decay = transition.decayFunction( decayFunction, self )
            probability = self.simDesc.get_probability_for_probability_id( transition.probability )
            self.v_print( lambda : 'Considering target action: %s, probability %s, decay %g' % (transition.target, probability.id, decay) )

            nextTarget = self.get_transition_by_probability_definition( probability, decay, H1, transition )

            # Notify observers of transition considering ending
            self.notifyObservers( TransitionConsiderEnd( self.currentState, transition ) )

            if nextTarget != None:
                # Notify observers of a transition being accepted
                self.notifyObservers( TransitionAccepted( self.currentState, transition ) )
                return nextTarget
            else:
                # Notify observers of a transition being rejected
                self.notifyObservers( TransitionRejected( self.currentState, transition ) )
                continue

        # Didn't hit any transition.
        # Use calculated target as fallback.
        if H1.calculateTarget == None:
            raise TransitionError.TransitionError( 'Unable to determine next transition for action %s. Please check simulation description.' % self.currentState.prevAction )

        # Notify observers of the fallback transition being accepted
        self.notifyObservers( TransitionAccepted( self.currentState, H1.calculateTarget ) )
        return H1.calculateTarget

    def advance(self):
        '''
        Advances the simulation one step:
        1. Calculates the next transition if not yet done
        2. Follows the next transition as specified by current state
        3. Creates a new simulation state object for the next state
        4. Runs the triggers associated with next transition's target action
        5. Calculates gains and costs
        Returns True if the next transition is not final (simulation should continue).
        Otherwise False.
        '''

        # Notify observers of transition calculation beginning
        self.notifyObservers( NextTransitionCalculationBegin( self.currentState ) )

        try:
            if self.currentState.nextTransition == None:
                self.currentState.nextTransition = self.get_next_transition()
        except UnknownDocumentError.UnknownDocumentError:
            # No document for current rank was found. Check if
            # the reason is because we ran out of results.
            if self.get_current_rank() > self.get_current_results_length():
                return False
            raise

        # Notify observers of transition calculation ending
        self.notifyObservers( NextTransitionCalculationEnd( self.currentState ) )

        nextAction = None
        if hasattr( self.currentState.nextTransition, 'target' ) and (
            self.currentState.nextTransition.target != None):
            nextAction = self.simDesc.get_action_by_id( self.currentState.nextTransition.target )

        # Notify observers of current transition beginning
        self.notifyObservers( TransitionBegin( self.currentState ) )

        # Currently, transitions are instantaneous


        # Notify observers of current transition ending
        self.notifyObservers( TransitionEnd( self.currentState ) )

        self.record_transition_statistics( self.currentState.prevAction, self.currentState.nextTransition.target )
        self.history.append( self.currentState )
        self.currentState = self.currentState.get_copy()

        if nextAction != None:

            # Notify observers of current action beginning
            self.notifyObservers( ActionBegin( self.currentState ) )

            triggers.run_triggers( nextAction, self )
            if hasattr( nextAction, 'cost' ) and nextAction.cost != None:
                cost = self.simDesc.get_cost_callback_by_id( nextAction.cost )
                if hasattr( cost, 'callback' ) and cost.callback != None:
                    try:
                        self.currentState.cumulatedCost += \
                                self.config.get_cost_callbacks()[ cost.callback.name ](
                                    self, **cost.callbackArgs )
                    except KeyError:
                        raise CallbackError(
                            'Cost callback \'%s\' not found. Check callback mapping. Available callbacks: %s' \
                            % ( cost.callback.name, repr(self.config.get_cost_callbacks().keys())))
                else:
                    self.currentState.cumulatedCost += cost.value_

            if hasattr( nextAction, 'gain' ) and nextAction.gain != None:
                gain = self.simDesc.get_gain_callback_by_id( nextAction.gain )
                if hasattr( gain, 'callback' ) and gain.callback != None:
                    try:
                        self.currentState.cumulatedGain += self.config.get_gain_callbacks()[ gain.callback.name ](
                                self, **gain.callbackArgs )
                    except KeyError:
                        raise CallbackError(
                            'Gain callback \'%s\' not found. Check callback mapping. Available callbacks: %s' \
                            % ( gain.callback.name, repr(self.config.get_gain_callbacks().keys())))
                else:
                    self.currentState.cumulatedGain += gain.value_

                self.calculate_derived_gains()

            # Notify observers of current action ending
            self.notifyObservers( ActionEnd( self.currentState ) )

        if nextAction.final:
            return False

        return True

