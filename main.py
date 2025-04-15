import cmd
from callcenter import Callcenter

class CallcenterCMD(cmd.Cmd):
    intro = "Call center simulation. Type help or ? to list commands.\n"
    prompt = '(callcenter) '

    def __init__(self):
        super().__init__()
        self.center = Callcenter(['A', 'B'])

    def do_call(self, arg):
        "call <id> : Receives a new call"
        self.center.receive_call(arg)

    def do_answer(self, arg):
        "answer <operator_id> : Operator answers a call"
        self.center.answer(arg)

    def do_reject(self, arg):
        "reject <operator_id> : Operator rejects a call"
        self.center.reject(arg)

    def do_hangup(self, arg):
        "hangup <call_id> : Finish a call"
        self.center.hangup(arg)

    def do_exit(self, arg):
        "exit : Exit the simulation"
        print("Goodbye!")
        return True

if __name__ == '__main__':
    CallcenterCMD().cmdloop()
