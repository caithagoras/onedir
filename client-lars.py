from twisted.internet import reactor, protocol
import os,json

fname="asdf.png"

'''
class DataObject():

    f = file
    fname = ''
    fsize = 0


    def __init__(self, fname, format = 'binary'): 
        self.fname = fname
        if format != 'binary':
            print 'unsupported file write format in DataObject constructor'
        self.f = open(fname, 'rb')
        '''


class EchoClient(protocol.Protocol):

    def connectionMade(self):
        print 'establishing connection with server'
        fsize = os.path.getsize(fname) 
        self.transport.write(json.dumps({'file':{'name': fname, 'size':fsize}}))


    def sendFile(self):
        print 'sending file: ' + fname 
        f = open(fname,"rb")
        self.transport.write(f.read())
        f.close()
        print "closing conn"
        self.transport.loseConnection()

    def dataReceived(self, data):
        "As soon as any data is received"
        print "Server said: ", data
        self.sendFile()

    def connectionLost(self, reason):
        print "connection loseConnectiont"

class EchoFactory(protocol.ClientFactory):
    protocol = EchoClient

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed - goodbye!"
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print "Connection lost - goodbye!"
        reactor.stop()


# this connects the protocol to a server runing on port 8000
def main():
    f = EchoFactory()
    #reactor.connectTCP("localhost", 8002, f)
    reactor.connectTCP('172.25.203.215', 8002, f)
    reactor.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()

#joubin: 172.25.203.215
#home: 10.0.1.41