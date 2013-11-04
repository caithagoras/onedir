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


class TestHook:

    def getOutput(self, msg):
        print(msg)

#hook = TestHook()
#manager = CoordinationManager()
#manager.init(hook)
#time.sleep(3)
#hook.getOutput(manager.createAccount("Bobvo", "password", "true"))
#print manager.createAccount("Bob", "password", "true")
#time.sleep(3)
#hook.getOutput(manager.createAccount("Bob", "password", "false"))
#time.sleep(3)
#hook.getOutput(manager.login("Bob", "abc"))
#time.sleep(3)
#hook.getOutput(manager.login("Bob", "password"))
#time.sleep(3)
#hook.getOutput(manager.createAccount("Bobvo", "password", "true"))


class InputManager:

    hook = TestHook()
    CoManager = CoordinationManager()
    CoManager.init(hook)
    input = ""

    def parse(self):
        while self.input != "quit":
            if self.input == "help":
                print "===Commands===\nlogin\ncreate account\nquit\n"
            elif self.input == "login":
                user = raw_input("Username: ")
                password = raw_input("Password: ")
                self.hook.getOutput(self.CoManager.login(user, password))
            elif self.input == "create account":
                user = raw_input("Username: ")
                password = raw_input("Password: ")
                admin = raw_input("Admin: ")
                self.hook.getOutput(self.CoManager.createAccount(user, password, admin))
            else:
                print "Not a valid command - please try again."
            self.start()
        if self.input == "quit":
            print "Quitting now."
            sys.exit()

    def start(self):
        time.sleep(2)
        self.input = raw_input("-------------------------\nWhat would you like to do?\nType "
                               "'help' for possible commands or 'quit' to quit\n")
        self.parse()

reader = InputManager()
reader.start()

