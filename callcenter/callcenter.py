from collections import deque
from twisted.internet import reactor
from callcenter.operatorClass import Operator
from callcenter.call import Call

class CallCenter:
    def __init__(self, operator_ids):
        self.operators = {op_id: Operator(op_id) for op_id in operator_ids}
        self.queue = deque()
        self.calls = {} 
        self.timeouts = {}  # <call_id>: timeout_handle

    def receive_call(self, call_id):
        msg = f"Call {call_id} received"
        call = Call(call_id)
        self.calls[call_id] = call
        dispatch_msg = self._dispatch_call(call)
        return f"{msg}\n{dispatch_msg}"

    def _dispatch_call(self, call, ignore_operator_id=None):
        for operator in self.operators.values():
            if operator.state == 'available' and operator.id != ignore_operator_id:
                operator.state = 'ringing'
                operator.current_call = call
                call.state = 'ringing'
                self._set_timeout(call.id, operator.id)
                return f"Call {call.id} ringing for operator {operator.id}"
        self.queue.append(call)
        return f"Call {call.id} waiting in queue"


    def _set_timeout(self, call_id, operator_id, timeout_seconds=10):
        def timeout_fn():
            operator = self.operators.get(operator_id)
            call = self.calls.get(call_id)

            if operator and operator.current_call == call and call.state == 'ringing':
                operator.state = 'available'
                operator.current_call = None
                print(f"Call {call_id} ignored by operator {operator_id}")

                dispatch_msg = self._dispatch_call(call, ignore_operator_id=operator_id)
                print(dispatch_msg)

        self.timeouts[call_id] = reactor.callLater(timeout_seconds, timeout_fn)



    def _cancel_timeout(self, call_id):
        timeout = self.timeouts.pop(call_id, None)
        if timeout and timeout.active():
            timeout.cancel()

    def answer(self, operator_id):
        operator = self.operators.get(operator_id)
        if operator and operator.state == 'ringing':
            call = operator.current_call
            self._cancel_timeout(call.id)
            call.state = 'answered'
            operator.state = 'busy'
            return f"Call {call.id} answered by operator {operator.id}"
        return f"Operator {operator_id} cannot answer at this time."

    def reject(self, operator_id):
        operator = self.operators.get(operator_id)
        if operator and operator.state == 'ringing':
            call = operator.current_call
            self._cancel_timeout(call.id)
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
                    self._cancel_timeout(call.id)
                    operator.state = 'available'
                    operator.current_call = None
                    queue_msg = self._check_queue()
                    return f"Call {call.id} finished and operator {operator.id} available" + (
                        f"\n{queue_msg}" if queue_msg else ""
                    )

        elif call.state == 'ringing':
            for operator in self.operators.values():
                if operator.current_call == call:
                    self._cancel_timeout(call.id)
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
