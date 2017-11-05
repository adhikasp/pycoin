from collections import defaultdict
import hashlib
import json
import time


MINER_REWARD = 1
MAX_TX_PER_BLOCK = 5

class BlockChain:
	def __init__(self):
		self.pending_transaction = []
		self.state = defaultdict(lambda: 0)
		self.head = None

	def last_block(self):
		return self.head

	def mine_block(self, miner):
		"""
		Mine a block
		"""
		# Miner reward
		self.pending_transaction.append(
			Transaction('0', miner, MINER_REWARD))

		# Prepare and validate tx
		inserted_tx = []
		while (len(inserted_tx) < MAX_TX_PER_BLOCK 
				and len(self.pending_transaction)):
			tx = self.pending_transaction.pop(0)
			if self.apply_tx(tx):
				inserted_tx.append(tx)

		# Archive the tx on the blockchain
		new_block = Block(inserted_tx, self.head)
		self.head = new_block

	def apply_block(self, block):
		"""
		Apply a block to current blockchain
		"""
		old_state = self.state.copy()
		assert block.previous_block == self.head
		for tx in block.transactions:
			if not all(self.apply_tx(tx)):
				print("Block '{}' contain invalid tx. "
					  'Reverting blockchain.')
				self.state = old_state
				return False
		self.head = block
		return True

	def apply_tx(self, tx):
		state = self.state.copy()
		if self.is_valid_transaction(tx):
			state[tx.sender] -= tx.amount
			state[tx.recepient] += tx.amount
			self.state = state
			return True
		return False

	def is_valid_transaction(self, transaction):
		if transaction.sender == '0':
			if transaction.amount != MINER_REWARD:
				print('Block miner reward is not right.')
				return False
		elif self.state[transaction.sender] < transaction.amount:
			print("Insufficient balance for account '{}'"
				  .format(transaction.sender))
			return False
		return True

	def new_transaction(self, transaction):
		self.pending_transaction.append(transaction)

	def print_chain(self):
		print('Current state')
		json_dump = json.dumps(
			self.state, 
			sort_keys=True, 
			default=lambda o: o.__dict__, 
			indent=4,)
		
		print('Blockchain')
		current_block = self.head
		while current_block != None:
			json_dump = json.dumps(
				current_block, 
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
b.mine_block('saya')
b.mine_block('saya')
b.new_transaction(Transaction('saya', 'dia', 1))
