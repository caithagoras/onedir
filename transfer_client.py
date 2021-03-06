from twisted.internet import reactor, protocol, defer
from twisted.protocols import basic
import os, json


class TransferCancelled(Exception):
    """Exception for a user cancelling a transfer"""
    pass

class FileIOClient(basic.LineReceiver):

    def __init__(self, path, upload, file_key, controller):
        self.path = path
        self.upload = upload
        self.file_key = file_key
        self.controller = controller

        self.infile = open(self.path, 'rb')
        self.insize = os.stat(self.path).st_size

        self.result = None
        self.completed = False

        self.controller.file_sent 	= 0
        self.controller.file_size 	= self.insize
        self.controller.total_sent 	= 0
        self.controller.cancel 		= False

    def _monitor(self, data):
        self.controller.file_sent 	+= len(data)
        self.controller.total_sent 	+= len(data)

        # Check with controller to see if we've been cancelled and abort
        # if so.
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
        #self.transport.loseConnection()

    def connectionMade(self):
    	print 'FileIOClient:connectionMade'
    	print 'debug: ' +  str(self.upload)

        if not self.upload:
            print 'FileIOClient:download requested'
            message = 'download'
            filesize = 0

    	if self.upload:
	    	print 'FileIOClient:upload requested'
	    	message = 'upload'
	    	filesize = self.insize

        self.transport.write('%s %s %s\r\n' %(message,  str(self.path), filesize))
        if self.upload:
			sender = basic.FileSender()
			sender.CHUNK_SIZE = 2 ** 16
			d = sender.beginFileTransfer(self.infile, self.transport, self._monitor)
			d.addCallback(self.cbTransferCompleted)
    
    def lineReceived(self, line):
            print 'FileIOProtocol:lineReceived ' + line
            command = []
            command = line.split(' ')
            print command
            if command[0] == 'download':      
                file_path = command[1]
                self.size = command[2]

                file_path = 'downloaded_' + file_path

                # if not os.path.isdir(file_path):
                #     os.makedirs(file_path)

                # self.outfilename = os.path.join('', file_path)
                self.infilename = file_path

                print 'FileIOProtocol:lineReceived downloading into ' + str(self.infilename)
                try:
                    self.outfile = open(self.infilename,'wb')
                except Exception, value:
                    print 'FileIOProtocol:lineReceived Unable to open file: "' + self.infilename + '"' +  str(value)
                    self.transport.loseConnection()
                    return

                self.remain = int(self.size)
                print 'FileIOProtocol:lineReceived Entering raw mode'
                self.setRawMode()


    def rawDataReceived(self, data):
        self.remain -= len(data)
        print 'remaining data: ' + str(self.remain)
        self.outfile.write(data)
        if self.remain == 0:
            if self.outfile:
                self.outfile.close()
                print 'FileIOProtocol:transfer complete'



	def connectionLost(self, reason):
		print 'FileIOClient:connectionLost'
		basic.LineReceiver.connectionLost(self, reason)
		self.infile.close()
		if self.completed:
		    self.controller.completed.callback(self.result)
		else:
		    self.controller.completed.errback(reason)

class FileIOClientFactory(protocol.ClientFactory):

    protocol = FileIOClient

    def __init__(self, path, upload_bool, file_key, controller):
        self.path = path
        self.upload = upload_bool

        self.file_key = file_key
        self.controller = controller
        
    def clientConnectionFailed(self, connector, reason):
        protocol.ClientFactory.clientConnectionFailed(self, connector, reason)
        self.controller.completed.errback(reason)

    def buildProtocol(self, addr):
        p = self.protocol(self.path, self.upload, self.file_key,
                          self.controller)
        p.factory = self
        return p


class TransferClient:

    #__init__(self, ip_address, port):


	def _uploadOne(self, ip_address, port, path):
	    self.completed = defer.Deferred()
	    f = FileIOClientFactory(path, True, 2, self)
	    reactor.connectTCP(ip_address, port, f)
	    return self.completed


	def _downloadOne(self, ip_address, port, path):
		self.completed = defer.Deferred()
		f = FileIOClientFactory(path, False, 2, self)
		reactor.connectTCP(ip_address, port, f)
		return self.completed