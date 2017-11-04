import hashlib
import json
import time


class BlockChain:
	def __init__(self):
		self.pending_transaction = []
		self.head = None

	def last_block(self):
		return self.head

	def new_block(self):
		new_block = Block(self.pending_transaction, self.head)
		self.pending_transaction = []
		self.head = new_block

	def new_transaction(self, transaction):
		self.pending_transaction.append(transaction)

	def print_chain(self):
		current_block = self.head
		while current_block != None:
			json_dump = json.dumps(
				self.__dict__, 
				sort_keys=True, 
				default=lambda o: o.__dict__, 
				indent=4,)
			print(json_dump)
			current_block = current_block.previous_block


class Block:
	def __init__(self, transactions, previous_block):
		self.timestamp = time.time()
		self.transactions = transactions
		self.previous_block = previous_block
		self.hash = self.hashes()

	def hashes(self):
		json_dump = json.dumps(
			self.__dict__, 
			sort_keys=True, 
			default=lambda o: o.__dict__).encode()
		return hashlib.sha256(json_dump).hexdigest()


class Transaction:
	def __init__(self, sender, recepient, amount):
		self.sender = sender
		self.recepient = recepient
		self.amount = amount
		self.hash = self.hashes()

	def hashes(self):
		json_dump = json.dumps(self.__dict__, sort_keys=True).encode()
		return hashlib.sha256(json_dump).hexdigest()

b = BlockChain()
b.new_transaction(Transaction('saya', 'dia', 1))
b.new_block()
