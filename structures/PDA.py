from collections import deque

class PushDown:
    def __init__(self):
        ## so we have our token stack
        self.tape  = deque([])
        self.stack       = deque([])
        self.state_stack = deque([])
        
    def set_tape(self, data):
        self.tape = deque(data)
        
    def finite_control(self):
        pass

 
