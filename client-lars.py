from twisted.internet import reactor, protocol
import os,json

fname = "asdf.png"


class EchoClient(protocol.Protocol):

    def connectionMade(self):
        print 'establishing connection with server'
        fsize = os.path.getsize(fname) 
        self.transport.write(json.dumps({'name': fname, 'size':fsize}))

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


def main():
    f = EchoFactory()
    reactor.connectTCP('localhost', 8000, f)
    reactor.run()

if __name__ == '__main__':
    main()

#joubin: 172.25.203.215
#home: 10.0.1.41