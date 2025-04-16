import json
from twisted.internet import protocol, reactor
from callcenter.callcenter import CallCenter

class CallCenterServerProtocol(protocol.Protocol): # Defines a TCP protocol to handle each connecting client
    def connectionMade(self):
        # Creates the protocol and saves the conection in clients array
        self.factory.clients.append(self) 

    def dataReceived(self, data):
        try:
            message = json.loads(data.decode('utf-8')) # Converts JSON format to utf-8 {"command": "call", "id": "1"}
            command = message['command'] 
            id = message['id']
            response = self.handle_command(command, id) # Calls function that executes the command logic on the id
            self.transport.write(json.dumps({"response": response}).encode('utf-8')) # Returns "response (JSON)" to client
        except Exception as e:
            self.transport.write(json.dumps({"response": f"Error: {str(e)}"}).encode('utf-8'))

    def handle_command(self, command, id):
        center = self.factory.call_center # Callcenter instance
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
        self.factory.clients.remove(self) # Removes client from clients array when it disconnects

class CallCenterFactory(protocol.Factory): # "Factory" of TCP connections => Every time a client connects it create a new CallCenterServerProtocol
    def __init__(self): # Create a central with 2 operators 
        self.call_center = CallCenter(['A', 'B'])
        self.clients = [] # clients array that stores the active connections

    def buildProtocol(self, addr): # Creates a protocol instance and passes the factory to it
        proto = CallCenterServerProtocol()
        proto.factory = self
        return proto

if __name__ == '__main__':
    reactor.listenTCP(5678, CallCenterFactory())
    print("Call center server running on port 5678...")
    reactor.run() # Starts Twisted loop
