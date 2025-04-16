import json
from twisted.internet import protocol, reactor
from callcenter.callcenter import CallCenter

class CallCenterServerProtocol(protocol.Protocol):
    def connectionMade(self):
        self.factory.clients.append(self)

    def dataReceived(self, data):
        try:
            message = json.loads(data.decode('utf-8'))
            command = message['command']
            id = message['id']
            response = self.handle_command(command, id)
            self.transport.write(json.dumps({"response": response}).encode('utf-8'))
        except Exception as e:
            self.transport.write(json.dumps({"response": f"Error: {str(e)}"}).encode('utf-8'))

    def handle_command(self, command, id):
        center = self.factory.call_center
        if command == 'call':
            return center.receive_call(id)
        elif command == 'answer':
            return center.answer(id)
        elif command == 'reject':
            return center.reject(id)
        elif command == 'hangup':
            return center.hangup(id)
        return f"Unknown command: {command}"

    def connectionLost(self, reason):
        self.factory.clients.remove(self)

class CallCenterFactory(protocol.Factory):
    def __init__(self):
        self.call_center = CallCenter(['A', 'B'])
        self.clients = []

    def buildProtocol(self, addr):
        proto = CallCenterServerProtocol()
        proto.factory = self
        return proto

if __name__ == '__main__':
    reactor.listenTCP(5678, CallCenterFactory())
    print("Call center server running on port 5678...")
    reactor.run()
