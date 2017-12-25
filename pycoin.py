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

    def get_block(self, block_hash):
        block = self.head
        while block.hash != block_hash or block != None:
            block = block.previous_block

        if block is None:
            print("No block with hash '{}' found"
                  .format(block_hash))
            return False
        return block

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
               and self.pending_transaction):
            new_tx = self.pending_transaction.pop(0)
            if self.apply_tx(new_tx):
                inserted_tx.append(new_tx)

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
        json_dump = PycoinJsonEncoder.encode(
            self,
            indent=4)
       
        print('Blockchain')
        current_block = self.head
        while current_block != None:
            json_dump = PycoinJsonEncoder.encode(
                current_block,
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
        json_dump = PycoinHasherJsonEncoder.encode(
            self)
        return hashlib.sha256(json_dump).hexdigest()


class Transaction:
    def __init__(self, sender, recepient, amount):
        self.sender = sender
        self.recepient = recepient
        self.amount = amount
        self.hash = self.hashes()

    def hashes(self):
        json_dump = PycoinHasherJsonEncoder.encode(
            self)
        return hashlib.sha256(json_dump).hexdigest()


class PycoinHasherJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BlockChain):
            return {
                'head': self.head,
                'pending_transaction': self.pending_transaction,
                'state': self.state,
            }
        elif isinstance(obj, Block):
            if obj.previous_block:
                previous_block_hash = obj.previous_block.hash
            else:
                previous_block_hash = None
            return {
                'previous_block': previous_block_hash,
                'timestamp': self.timestamp,
                'transactions': self.transactions,
            }
        elif isinstance(obj, Transaction):{
                'amount': self.amount,
                'recepient': self.recepient,
                'sender': self.sender,
            }
        else:
            return JSONEncoder.default(self, obj)


if __name__ == '__main__':
    b = BlockChain()
    b.mine_block('saya')
    b.mine_block('saya')
    b.new_transaction(Transaction('saya', 'dia', 1))
    b.mine_block('saya')
    print(b.state)
    assert b.state['saya'] == 2
    assert b.state['dia'] == 1
