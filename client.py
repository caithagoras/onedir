from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol

class SendMsg(Protocol):
    
    def connectionMade(self):
        reactor.callLater(2,self.sendMessage, "validate\tTom\twrongPassword")
        print ("Connection made.")
        
    def sendMessage(self, msg):
        self.transport.write(msg)
        print ("Sent message")
        
    def dataReceived(self, data):
        if (data == "Login_accepted"):
            print("Login attempt succeeded. You are logged in.")
        elif (data == "Login_rejected"):
            print("Login attempt failed. You are not logged in.")

point = TCP4ClientEndpoint(reactor, "localhost", 3240)
d = connectProtocol(point, SendMsg())
reactor.run()
