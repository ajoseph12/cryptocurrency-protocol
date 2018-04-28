import os
import json


class DiskHandler(object):
	"""
	Dedicated object for file I/O
	
	"""
	def __init__(self):
		self.path = os.path.join(os.getcwd(),"blocks")
		self.file = os.path.join(self.path,".cheddar")

		if os.path.exists(self.path):
			self.dir = os.listdir(self.path)
			os.chdir(self.path)
			if not os.path.exists(self.file):
				open(".cheddar","a").close()
		else:
			os.mkdir(self.path)
			os.chdir(self.path)
			open(".cheddar","a").close()
			self.dir = os.listdir(self.path)

		self.last_block_on_disk = None

	def read_block(self,block_num = None):
		with open(".cheddar","r") as f:
			return f.read()

	def append_block(self,block):
		with open(".cheddar","a+") as f:
			f.write(block)
	def delete_blockchain(self): #deletes blockchain file
		os.remove(".cheddar")

