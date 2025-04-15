class Call:
    def __init__(self, id):
        self.id = id
        self.state = 'waiting' # 'waiting', 'ringing', 'answered', 'finished', 'missed'