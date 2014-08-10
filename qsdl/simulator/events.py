'''
Created on 20 Feb 2013

@author: teemu
'''

class Event:
    def __init__(self,eventId = None):
        self.eventId = eventId or Event.getEventId( self.__class__ )
        
    @staticmethod
    def getEventId( clazz ):
        return clazz.__name__

class SimulationStateEvent(Event):
    def __init__(self, state):
        Event.__init__(self)
        self.lastSimulationState = state
        
class TransitionEnd(SimulationStateEvent):
    def __init__(self, state):
        SimulationStateEvent.__init__(self,state)

class TransitionBegin(SimulationStateEvent):
    def __init__(self, state):
        SimulationStateEvent.__init__(self,state)

class NextTransitionCalculationBegin(SimulationStateEvent):
    def __init__(self, state):
        SimulationStateEvent.__init__(self,state)

class NextTransitionCalculationEnd(SimulationStateEvent):
    def __init__(self, state):
        SimulationStateEvent.__init__(self,state)

class ActionBegin(SimulationStateEvent):
    def __init__(self, state):
        SimulationStateEvent.__init__(self,state)

class ActionEnd(SimulationStateEvent):
    def __init__(self, state):
        SimulationStateEvent.__init__(self,state)

class TransitionEvent(SimulationStateEvent):
    def __init__(self, state, pyxbTransition):
        SimulationStateEvent.__init__(self, state)
        self.transition = pyxbTransition
        
class TransitionConsiderBegin(TransitionEvent):
    def __init__(self, state, pyxbTransition):
        TransitionEvent.__init__(self, state, pyxbTransition)
        
class TransitionConsiderEnd(TransitionEvent):
    def __init__(self, state, pyxbTransition):
        TransitionEvent.__init__(self, state, pyxbTransition)

class TransitionRejected(TransitionEvent):
    def __init__(self, state, pyxbTransition):
        TransitionEvent.__init__(self, state, pyxbTransition)

class TransitionAccepted(TransitionEvent):
    def __init__(self, state, pyxbTransition):
        TransitionEvent.__init__(self, state, pyxbTransition)

class ProbabilityCalculated(TransitionEvent):
    def __init__(self, state, pyxbTransition, probabilityValue):
        TransitionEvent.__init__(self, state, pyxbTransition)
        self.probabilityValue = probabilityValue
        