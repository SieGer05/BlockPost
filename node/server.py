import json
import time
import requests
from flask import Flask, request, jsonify

from blockchain.block import Block
from blockchain.blockchain import Blockchain

app = Flask(__name__)

blockchain = Blockchain()

peers = set()

@app.route('/new_transaction', methods=['POST'])
def new_transaction():
   """
   Endpoint to submit a new transaction to the blockchain
   """
   tx_data = request.get_json()
   required_fields = ["author", "content"]
   
   for field in required_fields:
      if not tx_data.get(field):
         return "Invalid transaction data", 400
   
   tx_data["timestamp"] = time.time()
   
   blockchain.add_new_transaction(tx_data)
   
   return "Success", 201

@app.route('/chain', methods=['GET'])
def get_chain():
   """
   Endpoint to return the node's copy of the blockchain
   """
   chain_data = []
   for block in blockchain.chain:
      chain_data.append(block.__dict__)
   
   return jsonify({
      "length": len(chain_data),
      "chain": chain_data,
      "peers": list(peers)
   })

@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
   """
   Endpoint to request the node to mine the unconfirmed transactions
   """
   result = blockchain.mine()
   if not result:
      return "No transactions to mine", 200
   else:
      chain_length = len(blockchain.chain)
      consensus()
      if chain_length == len(blockchain.chain):
         announce_new_block(blockchain.last_block)

      return f"Block #{blockchain.last_block.index} is mined.", 200

@app.route('/pending_tx', methods=['GET'])
def get_pending_tx():
   """
   Endpoint to get the list of unconfirmed transactions
   """
   return jsonify(blockchain.unconfirmed_transactions)

@app.route('/register_node', methods=['POST'])
def register_new_peers():
   """
   Endpoint to add new peers to the network
   """
   node_address = request.get_json().get("node_address")
   if not node_address:
      return "Invalid data", 400
   
   peers.add(node_address)
   
   return get_chain()

@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
   """
   Internally calls the 'register_node' endpoint to register current node with
   the remote node specified in the request, and sync the blockchain as well.
   """
   node_address = request.get_json().get("node_address")
   if not node_address:
      return "Invalid data", 400
   
   data = {"node_address": request.host_url}
   headers = {'Content-Type': "application/json"}
   
   response = requests.post(
      f"{node_address}/register_node",
      data=json.dumps(data),
      headers=headers
   )
   
   if response.status_code == 200:
      global blockchain
      global peers
      
      chain_dump = response.json()['chain']
      blockchain = create_chain_from_dump(chain_dump)
      peers.update(response.json()['peers'])
      return "Registration successful", 200
   else:
      return response.content, response.status_code

@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
   """
   Endpoint to add a block mined by someone else to the node's chain.
   The node first verifies the block and then adds it to the chain.
   """
   block_data = request.get_json()
   block = Block(
      block_data["index"],
      block_data["transactions"],
      block_data["timestamp"],
      block_data["previous_hash"],
      block_data["nonce"]
   )
   
   proof = block_data['hash']
   added = blockchain.add_block(block, proof)
   
   if not added:
      return "The block was discarded by the node", 400
   
   return "Block added to the chain", 201

def create_chain_from_dump(chain_dump):
   """
   Recreate the blockchain from a chain_dump
   """
   blockchain = Blockchain()
   
   for idx, block_data in enumerate(chain_dump):
      block = Block(
         block_data["index"],
         block_data["transactions"],
         block_data["timestamp"],
         block_data["previous_hash"],
         block_data["nonce"]
      )
      
      proof = block_data['hash']
      
      if idx > 0:  
         added = blockchain.add_block(block, proof)
         if not added:
            raise Exception("The chain dump is tampered!!")
      else: 
         block.hash = proof
         blockchain.chain[0] = block
   
   return blockchain

def consensus():
   """
   Our consensus algorithm. If a longer valid chain is found,
   our chain is replaced with it.
   """
   global blockchain
   
   longest_chain = None
   current_len = len(blockchain.chain)
   
   for node in peers:
      try:
         response = requests.get(f"{node}/chain")
         
         if response.status_code == 200:
            length = response.json()['length']
            chain = response.json()['chain']
            
            chain_obj = create_chain_from_dump(chain)
            
            if length > current_len and blockchain.check_chain_validity(chain_obj.chain):
               current_len = length
               longest_chain = chain_obj
      except:
         continue
   
   if longest_chain:
      blockchain = longest_chain
      return True
   
   return False

def announce_new_block(block):
   """
   A function to announce to the network once a block has been mined.
   Other blocks can simply verify the proof of work and add it to their
   respective chains.
   """
   for peer in peers:
      url = f"{peer}/add_block"
      try:
         requests.post(
            url,
            data=json.dumps(block.__dict__, sort_keys=True),
            headers={'Content-Type': "application/json"}
         )
      except:
         continue

if __name__ == '__main__':
   app.run(debug=True, port=8000)