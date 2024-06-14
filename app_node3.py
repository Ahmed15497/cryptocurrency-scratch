from flask import Flask, jsonify
from blockchain import Blockchain
from uuid import uuid4
import requests


app = Flask(__name__)

# creating an address for the node on port 5000
node_address = str(uuid4()).replace('-', '')


blockchain = Blockchain()

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender= node_address, receiver='Ahmed', amount=1)
    block = blockchain.create_block(proof, previous_hash)
    response = {
        'message': 'Congrats, you just mined a block',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
        'transactions': block['transactions']
    }
    return jsonify(response), 200




@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/is_chain_valid', methods=['GET'])
def is_chain_valid():
    response = {
        'Status': blockchain.is_chain_valid(),
    }
    return jsonify(response), 200


@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = requests.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    
    index = blockchain.add_transaction(sender= json['sender'], receiver=json['receiver'], amount=json['amount'])
    response = {
        'message': f"This transaction will be added to block: {index}"
    }

    return jsonify(response), 201


@app.route('/connect_node', methods=['POST'])
def connect_node():
    json = requests.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 400
    
    for node in nodes:
        blockchain.add_node(node)

    response = {
            'message': 'All nodes are connected',
            'total_nodes': list(blockchain.nodes)
    }

    return jsonify(response), 201


@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {
            'message': 'Chain is replaced by the longest one',
        }
    else:
        response = {
            'message': 'Current chain is the longest one',
        }        
    return jsonify(response), 200

if __name__ == '__main__':  
   app.run(port=5003, debug=False)