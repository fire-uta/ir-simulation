'''
Created on 17 Feb 2013

@author: teemu
'''

class Observer:
    def __init__(self):
        raise NotImplementedError

    def notify(self, observable, event):
        raise NotImplementedError

class SimulationStateRecorder(Observer):
    def __init__(self):
        pass

class TransitionRecorder(SimulationStateRecorder):
    def __init__(self):
        SimulationStateRecorder.__init__(self)

    def notify(self, observable, event):
        pass

class TransitionConsiderationRecorder(TransitionRecorder):
    def __init__(self):
        TransitionRecorder.__init__(self)

    def notify(self, observable, event):
        event.lastSimulationState.add_transition_considered( event.transition )

class ProbabilityRecorder( TransitionRecorder ):
    def __init__(self):
        TransitionRecorder.__init__(self)

    def notify(self, observable, event):
        event.lastSimulationState.add_transition_probability( event.transition, event.probabilityValue )

class DocumentIdRecorder( SimulationStateRecorder ):
    def __init__(self):
        SimulationStateRecorder.__init__(self)

    def notify(self, observable, event):
        event.lastSimulationState.set_document_id( event.docId )
