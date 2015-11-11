from time import time, sleep
import random
import pprint
import socket
import re
from gelfclient import UdpClient
from liblo import *

class Consumer(ServerThread):
	def __init__(self):
		try:
			self.gelf = UdpClient('162.219.4.234', port=12201, mtu=8000, source=socket.gethostname())
		except socket.error, (value,message): 
			print "Could not open socket: " + message 
		self.result = [0,0,0,0,0,0,0,0]    
		ServerThread.__init__(self, 1234)
		self.sum = 0
		self.zone = re.match(r'(.*)server',socket.gethostname()).group(1)

	@make_method('/power','ii')
	def foo_callback(self, path, args):
		bike,power = args
		self.result[bike] = power
		self.sum=0
		for n in self.result:
			self.sum += n

	@make_method(None, None)
	def fallback(self, path, args):
		print("received unknown message '%s'" % path)	

	def publish(self):
		print self.result,self.sum
		try:
			self.gelf.log(self.zone,sum=self.sum,details=self.result.__str__())
		except socket.error, (value,message): 
			print "Could not open socket: " + message 

try:
    server = Consumer()
except ServerError as err:
    print(err)
    sys.exit()

server.start()


while True:
	server.publish()
	sleep(60)

