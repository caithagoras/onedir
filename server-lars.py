from twisted.internet import reactor, protocol
import os,json

class FileTransferProtocol(protocol.Protocol):
    f = file
    fname = ''
    def dataReceived(self, data):
        try:
            try:
                json_data = json.loads(data)
                self.fname = 'copy_' + json_data['name']
                print 'filename: ' +  self.fname
                self.f = open(self.fname, 'wb')

                self.transport.write('ready for file!')
            except:
                print 'filedata incoming...length: ' + str(len(data))
                self.f.write(data)
        except:
            print 'unknown error' #happens if we don't receive json first

    def connectionLost(self, reason):
        print 'file transfer complete, closing connection'
        if self.f!=file:self.f.close()

def main():
    factory = protocol.ServerFactory()
    factory.protocol = FileTransferProtocol
    reactor.listenTCP(8000,factory)
    print "Listening on port 8000\n"
    reactor.run()

if __name__ == '__main__':
    main()