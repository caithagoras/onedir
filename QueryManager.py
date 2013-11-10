from Connection import Connection
from Connection import makeConnection
import time
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

    def connectCB(self, msg):
        self.outputHook.getOutput(msg)

    def createAccount(self, user, password, admin):
        if (user == None or password == None or admin == None): return "Must specify all login credentials"
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

    def removeUser(self, user):
        if (user == None): return "Must specify a user to remove"
        elif self.serverConnection.working: return "Connection is currently busy. Try again in a minute."
        else:

            self.serverConnection.removeUser(user, self.removeUserCB)
            return "Attempting to remove user. Please wait."

    def removeUserCB(self, success, msg):
        self.outputHook.getOutput(msg)

    def changePassword(self, user, password):
        if (user == None or password == None): return "Must specify a user and new password"
        elif self.serverConnection.working: return "Connection is currently busy. Try again in a minute."
        else:

            self.serverConnection.changePassword(user, password, self.changePasswordCB)
            return "Attempting to change password. Please wait."

    def changePasswordCB(self, success, msg):
        self.outputHook.getOutput(msg)

class TestHook:

    def getOutput(self, msg):
        print(msg)

hook = TestHook()
manager = CoordinationManager()
manager.init(hook)
time.sleep(2)
'''hook.getOutput(manager.createAccount("Bob", "password", "true"))
time.sleep(2)
hook.getOutput(manager.createAccount("Bob", "password", "false"))
time.sleep(2)
hook.getOutput(manager.login("Bob", "abc"))
time.sleep(2)'''
hook.getOutput(manager.login("Bob", "password"))
time.sleep(2)
hook.getOutput(manager.removeUser("Bobvo"))
'''time.sleep(2)
hook.getOutput(manager.createAccount("Bobvo", "password", "true"))
time.sleep(2)
hook.getOutput(manager.changePassword("Bobvo", "newPW"))'''
