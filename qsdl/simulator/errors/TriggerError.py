from qsdl.simulator.errors.IrsimError import IrsimError

class TriggerError(IrsimError):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr( self.value )

