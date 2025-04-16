from collections import deque
from callcenter.operatorClass import Operator
from callcenter.call import Call

class CallCenter:
    def __init__(self, operator_ids):
        self.operators = {op_id: Operator(op_id) for op_id in operator_ids}
        self.queue = deque()
        self.calls = {}

    def receive_call(self, call_id):
        msg = f"Call {call_id} received"
        call = Call(call_id)
        self.calls[call_id] = call
        dispatch_msg = self._dispatch_call(call)
        return f"{msg}\n{dispatch_msg}"

    def _dispatch_call(self, call):
        for operator in self.operators.values():
            if operator.state == 'available':
                operator.state = 'ringing'
                operator.current_call = call
                call.state = 'ringing'
                return f"Call {call.id} ringing for operator {operator.id}"
        self.queue.append(call)
        return f"Call {call.id} waiting in queue"

    def answer(self, operator_id):
        operator = self.operators.get(operator_id)
        if operator and operator.state == 'ringing':
            call = operator.current_call
            call.state = 'answered'
            operator.state = 'busy'
            return f"Call {call.id} answered by operator {operator.id}"
        return f"Operator {operator_id} cannot answer at this time."

    def reject(self, operator_id):
        operator = self.operators.get(operator_id)
        if operator and operator.state == 'ringing':
            call = operator.current_call
            operator.state = 'available'
            operator.current_call = None
            dispatch_msg = self._dispatch_call(call)
            return f"Call {call.id} rejected by operator {operator.id}\n{dispatch_msg}"
        return f"Operator {operator_id} cannot reject at this time."

    def hangup(self, call_id):
        call = self.calls.get(call_id)
        if not call:
            return f"Call {call_id} not found."

        if call.state == 'answered':
            for operator in self.operators.values():
                if operator.current_call == call:
                    operator.state = 'available'
                    operator.current_call = None
                    queue_msg = self._check_queue()
                    return f"Call {call.id} finished and operator {operator.id} available" + (
                        f"\n{queue_msg}" if queue_msg else ""
                    )

        elif call.state == 'ringing':
            for operator in self.operators.values():
                if operator.current_call == call:
                    operator.state = 'available'
                    operator.current_call = None
                    queue_msg = self._check_queue()
                    return f"Call {call.id} missed" + (
                        f"\n{queue_msg}" if queue_msg else ""
                    )

        elif call.state == 'waiting':
            self.queue = deque(c for c in self.queue if c.id != call_id)
            return f"Call {call.id} missed"

        return f"Call {call.id} is in an unknown state."

    def _check_queue(self):
        if self.queue:
            next_call = self.queue.popleft()
            return self._dispatch_call(next_call)
        return ""
