import json
from twisted.internet import reactor, protocol

class CallCenterClientProtocol(protocol.Protocol):
    def connectionMade(self):
        print("Connected to call center server.")
        self.send_input()

    def dataReceived(self, data):
        response = data.decode('utf-8')
        try:
            parsed = json.loads(response)
            print(f"(server) {parsed['response']}")
        except json.JSONDecodeError:
            print(f"(server) Invalid response: {response}")
        self.send_input()

    def send_input(self):
        user_input = input("(client) Enter command (call/answer/reject/hangup) and ID (e.g. 'call 1'): ")
        try:
            parts = user_input.strip().split()
            if len(parts) != 2:
                print("Invalid format. Use: command id")
                self.send_input()
                return

            command, id = parts
            payload = json.dumps({"command": command, "id": id})
            self.transport.write(payload.encode('utf-8'))

        except Exception as e:
            print(f"Error preparing message: {e}")
            self.send_input()

class CallCenterClientFactory(protocol.ClientFactory):
    def buildProtocol(self, addr):
        return CallCenterClientProtocol()

    def clientConnectionFailed(self, connector, reason):
        print("Connection failed.")
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print("Connection lost.")
        reactor.stop()

if __name__ == '__main__':
    reactor.connectTCP("localhost", 5678, CallCenterClientFactory())
    reactor.run()
