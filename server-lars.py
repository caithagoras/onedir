from twisted.internet import reactor, protocol
import os,json

class FileTransferProtocol(protocol.Protocol):
    f = file
    fname = ''
    def dataReceived(self, data):
        try:
            try:
                print format(json.loads(data))

                print 'data format: ' + data
                self.fname = data[data.find('"name":') : data.find(',')-1]
                self.fname = self.fname[9:]
                print 'filename: ' +  self.fname
                self.f = open(self.fname, 'wb')

                self.transport.write('ready for file!')
            except:
                print 'filedata incoming...'
                self.f.write(data)
                print '\t\t\t\twrote a data packet to ' + self.fname
        except:
            print 'unknown error' #happens if we don't receive json first

    def connectionLost(self, reason):
        print 'file transfer complete, closing connection'
        if self.f!=file:self.f.close()

def main():
    print 'begin'
    #running protocpl on port 8002. 
    factory = protocol.ServerFactory()
    factory.protocol = FileTransferProtocol
    reactor.listenTCP(8002,factory)
    print "Listening on port 8002\n"
    reactor.run()


# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()