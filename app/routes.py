import datetime
import json

import requests
from flask import render_template, redirect, request

from app import app

CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"

posts = []

def fetch_posts():
   """
   Function to fetch the chain from a blockchain node, parse the
   data, and store it locally.
   """
   try:
      get_chain_address = f"{CONNECTED_NODE_ADDRESS}/chain"
      response = requests.get(get_chain_address)
      if response.status_code == 200:
         content = []
         chain = json.loads(response.content)
         for block in chain["chain"]:
               for tx in block["transactions"]:
                  tx["index"] = block["index"]
                  tx["hash"] = block["hash"] if "hash" in block else ""
                  content.append(tx)

         global posts
         posts = sorted(
               content,
               key=lambda k: k['timestamp'],
               reverse=True
         )
   except requests.exceptions.RequestException:
      pass

@app.route('/')
def index():
   """
   Render the index page with all posts
   """
   fetch_posts()
   
   return render_template(
      'index.html',
      title='Blockchain Content Sharing',
      posts=posts,
      node_address=CONNECTED_NODE_ADDRESS,
      readable_time=lambda timestamp: datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
   )

@app.route('/submit', methods=['POST'])
def submit_textarea():
   """
   Endpoint to create a new transaction via our application
   """
   post_content = request.form["content"]
   author = request.form["author"]
   
   post_object = {
      'author': author,
      'content': post_content,
   }
   
   new_tx_address = f"{CONNECTED_NODE_ADDRESS}/new_transaction"
   
   try:
      requests.post(
         new_tx_address,
         json=post_object,
         headers={'Content-type': 'application/json'}
      )
   except requests.exceptions.RequestException:
      return redirect('/')
   
   return redirect('/')