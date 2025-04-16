class Call:
    def __init__(self, id):
        self.id = id
        self.state = 'waiting' # 'waiting', 'ringing', 'answered', 'finished', 'missed'

        '''
        
        waiting: waiting in queue
        ringing: being handed over to an operator
        answered: answered by an operator
        finished: ended normally
        missed: hang up before answering
        
        '''