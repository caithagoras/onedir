from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
import os.path


class SendMsg(Protocol):

    user = ""
    password = ""

    def connectionMade(self):
        global user
        global password
        if os.path.isfile("Login.txt"):            # if login info has been saved, see if they want to use it
            useCredentials = raw_input("Do you want to use your saved information? Enter 'y' for yes or 'n' for no: ")
            if useCredentials == 'y':
                myFile = open("Login.txt", 'rb')
                credentials = myFile.read()
                #print credentials
                pieces = credentials.split("\t")
                hide = ""
                for index in range(len(pieces[3])):
                    hide += "*"
                print "Username: " + pieces[2] + "\nPassword: " + hide
                reactor.callLater(2, self.sendMessage, credentials)
            elif useCredentials == 'n':
                os.remove("Login.txt")
                option = raw_input("Enter 'n' for new user or 'u' for existing user: ")
                if option == 'n':
                    print "Creating new user!"
                elif option == 'u':
                    print "Enter your credentials!"
                user = raw_input("Username: ")
                password = raw_input("Password: ")
                reactor.callLater(2, self.sendMessage, "validate\t" + option + "\t" + user + "\t" + password)
                #reactor.callLater(2,self.sendMessage, "validate\tTom\tpassword123")
                print "Connection made."
        
    def sendMessage(self, msg):
        self.transport.write(msg)
        #print ("Sent message")
        
    def dataReceived(self, data):
        if data == "Login_accepted":
            print "Login attempt succeeded. You are logged in."
            if not os.path.isfile("Login.txt"):
                auto = raw_input("Would you like to automatically log in next time? Enter 'y' for yes or 'n' for no: ")
                if auto == 'y':
                    self.logIn()
                print "Information saved."
        elif data == "Login_rejected":
            print("Login attempt failed. You are not logged in.")

    def logIn(self):
        myFile = open("Login.txt", 'wb')
        myFile.write("validate\t" + 'u' + "\t" + user + "\t" + password)
        myFile.close()

point = TCP4ClientEndpoint(reactor, "localhost", 3240)
d = connectProtocol(point, SendMsg())
reactor.run()
