import json
from twisted.internet import reactor, protocol

class CallCenterClientProtocol(protocol.Protocol):
    def connectionMade(self):
        print("Connected to call center server.")
        self.send_input() # Requests firts command for user

    def dataReceived(self, data): # Called when server responds
        response = data.decode('utf-8')
        try:
            parsed = json.loads(response)
            print(f"(server) {parsed['response']}")
        except json.JSONDecodeError:
            print(f"(server) Invalid response: {response}")
        self.send_input()

    def send_input(self): # Prompts user input in the expected format.
        user_input = input("(client) Enter command (call/answer/reject/hangup) and ID (e.g. 'call 1'): ")
        try:
            parts = user_input.strip().split() # Removes spaces and splits the string into parts => ["call", "1"]
            if len(parts) != 2: # Verifies correct format
                print("Invalid format. Use: command id")
                self.send_input()
                return

            command, id = parts # Unpack the "parts" array
            payload = json.dumps({"command": command, "id": id}) # Serialize the object into json string
            self.transport.write(payload.encode('utf-8')) # Sends command to server

        except Exception as e:
            print(f"Error preparing message: {e}")
            self.send_input()

class CallCenterClientFactory(protocol.ClientFactory): # Creates client's protocol instance
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
