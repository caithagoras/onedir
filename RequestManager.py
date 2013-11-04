from twisted.internet.protocol import Protocol, Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
import os.path

USER_DATABASE_FNAME = "users.db"

userDatabase = {}
if os.path.isfile(USER_DATABASE_FNAME):
    users = open(USER_DATABASE_FNAME, "r")
    for line in users:
        pieces = line.split("\n")[0].split("\r")[0].split(" ")
        print(pieces)
        if (len(pieces) == 3): userDatabase[pieces[0]] = [pieces[1], pieces[2]=="True"]
    users.close()

class UserConnection(Protocol):

    authenticated = False
    admin = False
    username = ""
    
    def connectionMade(self):
        print("Connection made")

    def connectionLost(self, reason):
        print("Connection lost")
        
    def dataReceived(self, data):
        print("==================================")
        print("Got message:\t" + data)
        pieces = data.split("\t")
        msgType = pieces[0]

        if (msgType == "login"):
            
            user = pieces[1]
            password = pieces[2]
            
            print("Login attempt:\nUser:\t\t" + user + "\nPassword:\t" + password)
            
            if userDatabase.has_key(user) and userDatabase[user][0] == password:
                self.authenticated = True
                self.username = user
                self.admin = userDatabase[user][1]
                self.transport.write("login_succeed\t" + user + "\t" + str(self.admin))
                print("Accepted")
            else:
                self.transport.write("login_fail\t" + user)
                print("Rejected")

        elif (msgType == "login_admin"):
            
            user = pieces[1]
            password = pieces[2]
            
            print("Admin login attempt:\nUser:\t\t" + user + "\nPassword:\t" + password)
            
            if userDatabase.has_key(user) and userDatabase[user][0] == password:
                if (userDatabase[user][1]):
                    self.authenticated = True
                    self.username = user
                    self.admin = True
                    self.transport.write("login_succeed\t" + user + "\t" + str(self.admin))
                    print("Accepted")
                else:
                    self.transport.write("login_fail_admin\t" + user)
                    print("Rejected")
            else:
                self.transport.write("login_fail\t" + user)
                print("Rejected")
                                     
        elif (msgType == "create"):
                                     
            user = pieces[1]
            password = pieces[2]
            isAdmin = (pieces[3] == "true")

            if (isAdmin and not self.admin):
                self.transport.write("create_bad_permission\t" + user)
                print("Rejected, not admin")
            elif userDatabase.has_key(user):
                self.transport.write("create_already_exists\t" + user)
                print("Rejected, user already exists")
            else:
                userDatabase[user] = [password, isAdmin]
                users = open(USER_DATABASE_FNAME, "a")
                users.write("\n" + user + " " + password + " " + str(isAdmin))
                users.close()
                self.transport.write("create_succeeded\t" + user)
                print("Accepted")

        if (self.authenticated):
            if (self.admin):
                if (msgType == "remove_user"):

                    user = pieces[1]

                    print("Remove user: " + user)
                    if (userDatabase.has_key(user)):
                        del userDatabase[user]
                        users = open(USER_DATABASE_FNAME, "r")
                        lines = users.readlines()
                        users.close()
                        users = open(USER_DATABASE_FNAME, "w")
                        for line in lines:
                            pieces = line.split("\n")[0].split("\r")[0].split(" ")
                            if pieces[0] != user:
                                users.write(line)
                        users.close()
                        self.transport.write("remove_user_succeeded\t" + user)
                    else:
                        self.transport.write("remove_user_not_exist\t" + user)

                if (msgType == "change_password"):
                    
                    user = pieces[1]
                    newPW = pieces[2]

                    print("Changing password for " + user + " to " + newPW)
                    
                    if (userDatabase.has_key(user)):
                        userDatabase[user][1] = newPW
                        users = open(USER_DATABASE_FNAME, "r")
                        lines = users.readlines()
                        users.close()
                        users = open(USER_DATABASE_FNAME, "w")
                        for line in lines:
                            pieces = line.split("\n")[0].split("\r")[0].split(" ")
                            if (len(pieces) == 3):
                                if pieces[0] == user: pieces[1] = newPW
                                users.write("\n" + pieces[0] + " " + pieces[1] + " " + pieces[2])
                        users.close()
                        self.transport.write("change_password_succeeded\t" + user)
                    else:
                        self.transport.write("change_password_not_exist\t" + user)
                    
            
        

class UserFactory(Factory):
    def buildProtocol(self, addr):
        return UserConnection()


reactor.listenTCP(3240, UserFactory())
reactor.run()
