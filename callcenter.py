from collections import deque
from operatorClass import Operator
from call import Call

class Callcenter:
    def __init__(self, operator_ids):
        self.operators = {op_id: Operator(op_id) for op_id in operator_ids}
        self.queue = deque()
        self.calls = {}

    def receive_call(self, call_id):
        print(f"Call {call_id} received")
        call = Call(call_id)
        self.calls[call_id] = call
        self._dispatch_call(call)

    def _dispatch_call(self, call):
        for operator in self.operators.values():
            if operator.state == 'available':
                operator.state = 'ringing'
                operator.current_call = call
                call.state = 'ringing'
                print(f"Call {call.id} ringing for operator {operator.id}")
                return
        self.queue.append(call)
        print(f"Call {call.id} waiting in queue")
    
    def answer(self, operator_id):
        operator = self.operators.get(operator_id)
        if operator and operator.state == 'ringing':
            call = operator.current_call
            call.state = 'answered'
            operator.state = 'busy'
            print(f"Call {call.id} answered by operator {operator.id}")
    
    def reject(self, operator_id):
        operator = self.operators.get(operator_id)
        if operator and operator.state == 'ringing':
            call = operator.current_call
            operator.state = 'available'
            operator.current_call = None
            print(f"Call {call.id} rejected by operator {operator.id}")
            self._dispatch_call(call)

    def hangup(self, call_id):
        call = self.calls.get(call_id)
        if not call:
            return

        if call.state == 'answered':
            for operator in self.operators.values():
                if operator.current_call == call:
                    operator.state = 'available'
                    operator.current_call = None
                    print(f"Call {call.id} finished and operator {operator.id} available")
                    self._check_queue()
                    return
                
        elif call.state == 'ringing':
            print(f"Call {call.id} missed")
            for operator in self.operators.values():
                if operator.current_call == call:
                    operator.state = 'available'
                    operator.current_call = None
                    self._check_queue()
                    return
                
        elif call.state == 'waiting':
            print(f"Call {call.id} missed")
            self.queue = deque(c for c in self.queue if c.id != call_id)
    
    def _check_queue(self):
        if self.queue:
            next_call = self.queue.popleft()
            self._dispatch_call(next_call)