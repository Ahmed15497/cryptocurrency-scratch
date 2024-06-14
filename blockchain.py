import datetime
import hashlib
import json
from flask import Flask, jsonify
import requests
from urllib.parse import urlparse


class Blockchain:

    def __init__(self):

        self.chain = []
        self.transactions = []
        self.nodes = set()
        self.create_block(proof=1, previous_hash='0')
        self.__leading_zeros = 4

    def create_block(self, proof, previous_hash):

        index = len(self.chain) + 1
        timestamp = str(datetime.datetime.now())
        block = {
            'index': index,
            'timestamp': timestamp,
            'proof': proof,
            'previous_hash': previous_hash,
            'transactions': self.transactions
            }

        self.transactions = []
        self.chain.append(block)

        return block

    def get_previous_block(self):
        return self.chain[-1]

    def __complex_problem(self, proof, previous_proof):
        equation = proof**2 - previous_proof**2
        return equation

    def __hash_proof(self, input_):
        print(input_)
        hash_operation = hashlib.sha256(str(input_).encode()).hexdigest()
        return hash_operation


    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            print(new_proof)
            hash_operation = self.__hash_proof(self.__complex_problem(new_proof, previous_proof))
            # check if it has four leading zeros
            if hash_operation[:self.__leading_zeros] == (self.__leading_zeros * '0'):
                check_proof = True
            else:
                new_proof += 1

        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain=None):
        if chain is None:
            chain = self.chain
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            # checks for previous correctness of previous hash
            if block['previous_hash'] != self.hash(previous_block):
                return False
            # check if the proof is correct and match four leading zeros
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = self.__hash_proof(self.__complex_problem(proof, previous_proof))
            if hash_operation[:self.__leading_zeros] != self.__leading_zeros * '0':
                return False
            # increase indexes for next iteration
            previous_block = block
            block_index += 1
        return True
    
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amount
        })

        previous_block = self.get_previous_block()

        return previous_block['index'] + 1



    def add_node(self, address):
        url_parsed = urlparse(address)
        self.nodes.add(url_parsed.netloc)

    def replace_chain(self):
        network = self.nodes 
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f"http://{node}/get_chain")
            if response.status_code == 200:
                # success
                chain_len = response.json()['length']
                chain = response.json()['chain']
                if (chain_len > max_length) and (self.is_chain_valid(chain)):
                    max_length = chain_len
                    longest_chain = chain

        if longest_chain:
            self.chain = longest_chain
            return True 
        
        return False


     