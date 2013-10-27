from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol

class SendMsg(Protocol):
    
    def connectionMade(self):
        option = raw_input("Enter 'n' for new user or 'u' for existing user: ")
        if option == 'n':
            print "Creating new user!"
        elif option == 'u':
            print "Enter your credentials-"
        user = raw_input("Username: ")
        pword = raw_input("Password: ")
        reactor.callLater(2,self.sendMessage, "validate\t" + user + "\t" + pword)
        #reactor.callLater(2,self.sendMessage, "validate\tTom\tpassword123")
        print "Connection made."
        
    def sendMessage(self, msg):
        self.transport.write(msg)
        #print ("Sent message")
        
    def dataReceived(self, data):
        if data == "Login_accepted":
            print("Login attempt succeeded. You are logged in.")
        elif data == "Login_rejected":
            print("Login attempt failed. You are not logged in.")

point = TCP4ClientEndpoint(reactor, "localhost", 3240)
d = connectProtocol(point, SendMsg())
reactor.run()

#things to add: check if userinfo.txt exists, create if it doesnt. read in information and attempt auto log in