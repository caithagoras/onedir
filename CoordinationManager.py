from Connection import Connection
from Connection import makeConnection
import time
import sys
import os.path

#====Build info====
WIN_BUILD = True
SERVER_IP = "localhost"
SERVER_PORT = 3240
fileDir = "/onedir"

if (WIN_BUILD):
    fileDir = "C:\onedir"

#====Class Def====


class CoordinationManager:

    outputHook = None
    serverConnection = None

    def init(self, output):
        #TODO: Initialize other subsystems
        self.outputHook = output
        self.serverConnection = makeConnection(SERVER_IP, SERVER_PORT, self.connectCB)

    #def init(self):
        #self.serverConnection = makeConnection(SERVER_IP, SERVER_PORT, self.connectCB)

    def connectCB(self, msg):
        self.outputHook.getOutput(msg)

    def createAccount(self, user, password, admin):
        if (user == None or password == None): return "Must specify all login credentials"
        elif self.serverConnection.working: return "Connection is currently busy. Try again in a minute."
        else:
            self.serverConnection.create(user, password, admin, self.createCB)
            return "Attempting to create user. Please wait."

    def createCB(self, success, msg):
        self.outputHook.getOutput(msg)

    def login(self, user, password):
        if (user == None or password == None): return "Must specify all login credentials"
        elif self.serverConnection.working: return "Connection is currently busy. Try again in a minute."
        else:

            self.serverConnection.login(user, password, self.loginCB)
            return "Attempting to login. Please wait."

    def loginCB(self, success, admin, msg):
        self.outputHook.getOutput(msg)

    def logout(self, user):
        if self.serverConnection.working:
            return "Connection is currently busy. Try again in a minute."
        else:
            self.serverConnection.logout(user, self.logoutCB)
            return "Attempting to logout. Please wait."

    def logoutCB(self, success, admin, msg):
        self.outputHook.getOutput(msg)


class TestHook:

    def getOutput(self, msg):
        print(msg)


class InputManager:

    hook = TestHook()
    CoManager = CoordinationManager()
    CoManager.init(hook)
    input = ""
    user = ""

    def parse(self):
        while self.input != "quit":
            if self.input == "help":
                print "===Commands===\nlogin\ncreate account\nsign out\nquit\n"
            elif self.input == "login":
                self.user = raw_input("Username: ")
                password = raw_input("Password: ")
                option = raw_input("Log in automatically (yes/no)? ")
                if option == "yes":
                    myFile = open("Login.txt", 'wb')
                    myFile.write(self.user + " " + password)
                    myFile.close()
                self.hook.getOutput(self.CoManager.login(self.user, password))
            elif self.input == "create account":
                self.user = raw_input("Username: ")
                password = raw_input("Password: ")
                admin = raw_input("Admin: ")
                self.hook.getOutput(self.CoManager.createAccount(self.user, password, admin))
            elif self.input == "sign out":
                #send message to server to log out
                self.hook.getOutput(self.CoManager.logout(self.user))
                os.remove("Login.txt")
                print "You are now signed out."
            else:
                print "Not a valid command - please try again."
            self.start()
        if self.input == "quit":
            print "Quitting now."
            sys.exit()

    def start(self):
        time.sleep(2)
        #print os.path.isfile("Login.txt")
        #print self.user == ""
        if os.path.isfile("Login.txt") and self.user == "":                 # if this file exists
            myFile = open("Login.txt", 'rb')            # open it
            credentials = myFile.read()                 # read it
            myFile.close()
            pieces = credentials.split("\n")[0].split("\r")[0].split(" ")  # separate it by delimiter
            self.user = pieces[0]
            password = pieces[1]
            print "Logging in as " + self.user + "."         # say you're logging in and attempt to do so
            self.hook.getOutput(self.CoManager.login(self.user, password))
            time.sleep(2)
        self.input = raw_input("-------------------------\nWhat would you like to do?\nType "
                               "'help' for possible commands or 'quit' to quit.\n")
        self.parse()

reader = InputManager()
reader.start()