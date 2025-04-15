class Operator:
    def __init__(self, id):
        self.id = id
        self.state = 'available' # 'available', 'ringing', 'busy'
        self.current_call = None