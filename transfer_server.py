from twisted.internet import reactor, protocol, defer
from twisted.protocols import basic
import os

class FileIOProtocol(basic.LineReceiver):

    def __init__(self, controller):
        self.outfile = None
        self.remain = 0
        self.completed = False

        self.controller = controller
        self.controller.file_sent   = 0
        self.controller.file_size   = 0
        self.controller.total_sent  = 0
        self.controller.cancel      = False

    def _monitor(self, data):
        self.controller.file_sent   += len(data)
        self.controller.total_sent  += len(data)

        if self.controller.cancel:
            print 'FileIOClient._monitor Cancelling'
            # Need to unregister the producer with the transport or it will
            # wait for it to finish before breaking the connection
            self.transport.unregisterProducer()
            self.transport.loseConnection()
            # Indicate a user cancelled result
            self.result = TransferCancelled('User cancelled transfer')
        return data

    def cbTransferCompleted(self, lastsent):
        print 'FileIOClient:transfer completed'
        self.completed = True
        self.transport.loseConnection()

    def lineReceived(self, line):
        print 'FileIOProtocol:lineReceived ' + line
        command = line.split(' ')

        if command[0] == 'upload':      
            file_path = command[1]
            self.size = command[2]

            file_path = 'uploaded_' + file_path

            # if not os.path.isdir(file_path):
            #     os.makedirs(file_path)

            # self.outfilename = os.path.join('', file_path)
            self.outfilename = file_path

            print 'FileIOProtocol:lineReceived uploading into ' + str(self.outfilename)
            try:
                self.outfile = open(self.outfilename,'wb')
            except Exception, value:
                print 'FileIOProtocol:lineReceived Unable to open file: "' + self.outfilename + '"' +  str(value)
                self.transport.loseConnection()
                return

            self.remain = int(self.size)
            print 'FileIOProtocol:lineReceived Entering raw mode'
            self.setRawMode()

        elif command[0] == 'download':
            file_path = command[1]
            print 'FileIOProtocol:LineReceived:opening file for download: ' + file_path
            if not os.path.exists(file_path):
                print 'FileIOProtocol: ERROR: file does not exist: ' + file_path
            
            self.outfile = open(file_path, 'rb')
            self.outsize = os.stat(file_path).st_size
            self.controller.file_size = self.outsize
            #except Exception:
            #    print 'FileIOProtocol:LineReceiver ERROR: opening file: ' + file_path

            self.transport.write('%s %s %s\r\n' %('download', str(file_path), self.outsize))

            print 'FileIOProtocol:lineReceived downloading as ' + str(file_path)

            self.outfilename = file_path

            sender = basic.FileSender()
            sender.CHUNK_SIZE = 2 ** 16
            d = sender.beginFileTransfer(self.outfile, self.transport, self._monitor)
            d.addCallback(self.cbTransferCompleted)
            
            print 'FileIOProtocol:lineReceived file sent'



    def rawDataReceived(self, data):
        self.remain -= len(data)
        print 'remaining data: ' + str(self.remain)
        self.outfile.write(data)
        if self.remain == 0:
            if self.outfile:
                self.outfile.close()
                print 'FileIOProtocol:transfer complete'

    def connectionMade(self):
        basic.LineReceiver.connectionMade(self)
        print'FileIOProtocol:connectionMade'

    def connectionLost(self, reason):
        basic.LineReceiver.connectionLost(self, reason)
        if self.outfile:
            self.outfile.close()

            if self.remain != 0:
                # Problem uploading - discard
                print 'FileIOProtocol:connectionLost remain'

                os.remove(self.outfilename)
        print 'FileIOProtocol:connectionLost'
        self.setLineMode()



class FileIOFactory(protocol.ServerFactory):
    protocol = FileIOProtocol

    def __init__(self, port, controller):
        self.port = port
        self.controller = controller

    def clientConnectionFailed(self, connector, reason):
        protocol.ServerFactory.serverConnectionFailed(self, connector, reason)
        self.controller.completed.errback(reason)

    def buildProtocol(self, addr):
        p = self.protocol(self.controller)
        p.factory = self
        return p



class TransferServer():

    def __init__(self, port):
        fileio = FileIOFactory(port, self)
        reactor.listenTCP(port, fileio)
        print 'Listening on port ' + str(port)


def main():

    server = TransferServer(8010)
    reactor.run()

if __name__ == '__main__':
    main()