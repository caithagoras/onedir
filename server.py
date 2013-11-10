from twisted.internet.protocol import Protocol, Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor


database = {"Tom": "password123",
            "Joe": "thisIsPassword",
            "Jim": "123456abcd"}


class UserConnection(Protocol):

    authenticated = False
    username = ""
    
    def connectionMade(self):
        print("Connection made")
        
    def dataReceived(self, data):
        print("Got message:\t" + data)
        pieces = data.split("\t")
        msgType = pieces[0]

        if msgType == "validate":
            option = pieces[1]
            user = pieces[2]
            password = pieces[3]
            print "Login attempt:\nUser:\t\t" + user + "\nPassword:\t" + password
            if option == 'n':
                print "Creating New User..."
                database[user] = password
            if database.has_key(user) and database[user] == password:
                authenticated = True
                username = user
                self.transport.write("Login_accepted");
                print "Accepted"
            else:
                self.transport.write("Login_rejected")
                print "Rejected"
        
        

class UserFactory(Factory):
    def buildProtocol(self, addr):
        return UserConnection()


reactor.listenTCP(3240, UserFactory())
reactor.run()
