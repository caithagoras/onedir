__author__='Leiqing Cai'

import local_engine
import sys

class CUI:

    authenticated=False

    def __init__(self):
        authenticated=True

    # Return True on success, False on failure
    def login(self,username,passwd):
        if not((isinstance(username,basestring) and isinstance(passwd,basestring))):
            return False

    # Try to automatically login
    # Return True on success, False on failure
    def autologin(self):
        return False

    # Return True on successful login, False on exit
    def prelogin_menu(self):
        print 'Onedir ver1.0'
        print 'Available command: signup, login, exit'
        while True:
            command=raw_input()
            if (command=='signup'):
                sys.stdout.write('Username: ')
                username=raw_input()
                sys.stdout.write('Password: ')
                passwd=raw_input();
                sys.stdout.write('Confirm password: ')
                passwdconfirm=raw_input();
                if passwd==passwdconfirm:
                    pass
            elif (command=='login'):
                sys.stdout.write('Username: ')
                username=raw_input()
                sys.stdout.write('Password: ')
                passwd=raw_input();
                if (self.login(username,passwd)==True):
                    authenticated=True
                    return True
            elif (command=='exit'):
                return False
            else:
                print 'Command not found'

    def start_seq(self):
        pass

    def main_menu(self):
        print 'Available command: settings, signout, exit'
        pass

    def start(self):
        if not (self.autologin()==True):
            if self.prelogin_menu()==False:
                return
            else:
                self.start_seq()
                self.main_menu()

