import time
from blockchain.block import Block

class Blockchain:
   difficulty = 2
   
   def __init__(self):
      """
      Constructor for the Blockchain class.
      """
      self.unconfirmed_transactions = []
      self.chain = []
      self.create_genesis_block()
   
   def create_genesis_block(self):
      """
      A function to generate genesis block and append it to the chain.
      The block has index 0, previous_hash as 0, and a valid hash.
      """
      genesis_block = Block(0, [], time.time(), "0")
      genesis_block.hash = genesis_block.compute_hash()
      self.chain.append(genesis_block)
   
   @property
   def last_block(self):
      """
      A quick pythonic way to retrieve the most recent block in the chain.
      Note that the chain will always consist of at least one block (genesis).
      """
      return self.chain[-1]
   
   def proof_of_work(self, block):
      """
      Function that tries different values of the nonce to get a hash
      that satisfies our difficulty criteria.
      """
      block.nonce = 0
      
      computed_hash = block.compute_hash()
      while not computed_hash.startswith('0' * Blockchain.difficulty):
         block.nonce += 1
         computed_hash = block.compute_hash()
      
      return computed_hash
   
   def add_block(self, block, proof):
      """
      A function that adds the block to the chain after verification.
      Verification includes:
      * Checking if the proof is valid.
      * The previous_hash referred in the block and the hash of the latest block
         in the chain match.
      """
      previous_hash = self.last_block.hash
      
      if previous_hash != block.previous_hash:
         return False
      
      if not self.is_valid_proof(block, proof):
         return False
      
      block.hash = proof
      self.chain.append(block)
      return True
   
   @classmethod
   def is_valid_proof(cls, block, block_hash):
      """
      Check if block_hash is valid hash of block and satisfies
      the difficulty criteria.
      """
      return (block_hash.startswith('0' * cls.difficulty) and
               block_hash == block.compute_hash())
   
   def add_new_transaction(self, transaction):
      """
      Adds a new transaction to the list of unconfirmed transactions.
      """
      self.unconfirmed_transactions.append(transaction)
   
   def mine(self):
      """
      This function serves as an interface to add the pending
      transactions to the blockchain by adding them to the block
      and figuring out proof of work.
      """
      if not self.unconfirmed_transactions:
         return False
      
      last_block = self.last_block
      
      new_block = Block(
         index=last_block.index + 1,
         transactions=self.unconfirmed_transactions,
         timestamp=time.time(),
         previous_hash=last_block.hash
      )
      
      proof = self.proof_of_work(new_block)
      self.add_block(new_block, proof)
      self.unconfirmed_transactions = []
      return new_block.index
   
   @classmethod
   def check_chain_validity(cls, chain):
      """
      A helper method to check if the entire blockchain is valid.
      """
      result = True
      previous_hash = "0"
      
      for block in chain:
         block_hash = block.hash
         delattr(block, "hash")
         
         if not cls.is_valid_proof(block, block_hash) or previous_hash != block.previous_hash:
               result = False
               break
         
         block.hash, previous_hash = block_hash, block_hash
      
      return result