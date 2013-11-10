from twisted.internet import reactor, protocol, defer
from twisted.protocols import basic
import os

class FileIOProtocol(basic.LineReceiver):

    def __init__(self):
        self.info = None
        self.outfile = None
        self.remain = 0
        self.crc = 0

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
            file_path = 'downloaded_' + file_path

            print 'FileIOProtocol:lineReceived downloading to ' + str(file_path)

            # if not os.path.isdir(file_path):
            #     os.makedirs(file_path)

            # self.outfilename = os.path.join('', file_path)
            self.outfilename = file_path

            if not os.path.exists(self.outfilename):
                print 'FileIOProtocol: ERROR: file does not exist: ' + self.outfilename

            try: 
                self.outfile = open(self.outfilename, 'rb')
                self.outsize = os.stat(self.outfilename).st_size
            except Exception:
                print 'FileIOProtocol: ERROR: opening file: ' + self.outfilename

            try:
                sender = basic.FileSender()
                sender.CHUNK_SIZE = 2 ** 16
                d = sender.beginFileTransfer(self.outfilename, self.transport,
                                             self._monitor)
                d.addCallback(self.cbTransferCompleted)
            except Exception: 
                print 'FileIOProtocol: ERROR: could not send file'



    def rawDataReceived(self, data):
        print 'asdf data  ' + str(self.remain)
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



class FileIOFactory(protocol.ServerFactory):
    protocol = FileIOProtocol

    def __init__(self, port):
        self.port = port


class TransferServer():

    def __init__(self, port):
        fileio = FileIOFactory(port)
        reactor.listenTCP(port, fileio)
        print 'Listening on port ' + str(port)


def main():

    server = TransferServer(8009)
    reactor.run()

if __name__ == '__main__':
    main()