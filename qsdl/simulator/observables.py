'''
Created on 17 Feb 2013

@author: teemu
'''

from qsdl.simulator.events import Event

class Observable:
    
    def __init__(self):
        self.observers = {};
    
    def registerObserver(self, eventClass, observer):
        eventId = Event.getEventId( eventClass )
        if not hasattr( self.observers, eventId ):
            self.observers[ eventId ] = []
        if self.observers[ eventId ].count( observer ) == 0:
            self.observers[ eventId ].append( observer )
        
    def unregisterObserver(self, eventId, observer):
        try:
            self.observers[ eventId ].remove( observer )
        except:
            pass
        
    def notifyObservers(self, event):
        try:
            observers = self.observers[ event.eventId ]
        except KeyError:
            return
        for observer in observers:
            observer.notify( self, event )
