import thread
from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol

def makeConnection(ip, port, connectCallback):
    connection = Connection()
    connection.callback = connectCallback
    point = TCP4ClientEndpoint(reactor, ip, port)
    d = connectProtocol(point, connection)
    thread.start_new_thread(startConnection, ())
    return connection

def startConnection():
    reactor.run(installSignalHandlers=0)
    

class Connection(Protocol):

    connected = False
    validated = False
    admin = False

    working = True
    process = "connect"
    callback = None

    user = ""
    password = ""

    def connectionMade(self):
        self.working = False
        self.connected = True
        self.callback("(Connection established with server.)")

    def sendMessage(self, msg):
        self.transport.write(msg)

    def dataReceived(self, data):
        pieces = data.split("\t")
        msgType = pieces[0]
        
        self.working = False
        if (self.callback != None):
            if (self.process == "login"):
                if(msgType == "login_fail"):
                    self.callback(False, False, "Login failed (bad username/password.")
                elif(msgType == "login_succeed"):
                    retUser = pieces[1]
                    self.validated = True
                    self.admin = (pieces[2] == "True")
                    self.callback(True, self.admin, "Login succeeded. Logged in as: " + retUser + ".")
            elif (self.process == "create"):
                retUser = pieces[1]
                if(msgType == "create_already_exists"):
                    self.callback(False, "Account creation failed. Username " + retUser + " already taken.")
                elif(msgType == "create_bad_permission"):
                    self.callback(False, "Account creation failed. Must be logged in as admin to create a new admin account.")
                elif(msgType == "create_succeeded"):
                    self.callback(True, "Account creation succeeded. " + retUser + " created.")
                
                
    def login(self, user, password, callback):
        self.working = True
        self.process = "login"
        self.callback = callback
        self.user = user
        self.password = password
        self.sendMessage("login\t" + user + "\t" + password)

    def logout(self, user, callback):
        self.working = True
        self.process = "logout"
        self.callback = callback
        self.user = user
        self.sendMessage("logout\t" + user)

    def create(self, user, password, admin, callback):
        self.working = True
        self.process = "login"
        self.callback = callback
        self.sendMessage("create\t" + user + "\t" + password + "\t" + admin)