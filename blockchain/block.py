import json
import time
from hashlib import sha256

class Block:
   def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
      """
      Constructor for the Block class.
      :param index: Unique ID of the block
      :param transactions: List of transactions
      :param timestamp: Time of generation of the block
      :param previous_hash: Hash of the previous block in the chain
      :param nonce: A counter used for the proof-of-work algorithm
      """
      self.index = index
      self.transactions = transactions
      self.timestamp = timestamp
      self.previous_hash = previous_hash
      self.nonce = nonce
      
   def compute_hash(self):
      """
      Returns the hash of the block instance by converting it to a JSON string.
      """
      block_string = json.dumps(self.__dict__, sort_keys=True)
      return sha256(block_string.encode()).hexdigest()