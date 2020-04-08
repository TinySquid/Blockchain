import random
import hashlib
import json

from time import time
from uuid import uuid4

from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain = []

        # tx's to be put into next block
        self.current_transactions = []

        # Genesis block
        self.new_block(proof=100, previous_hash=1)

    def new_block(self, proof, previous_hash):
        """
        Create a new Block in the Blockchain
​
        A block should have:
        * Index
        * Timestamp
        * List of current transactions
        * The proof used to mine this block
        * The hash of the previous block
​
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        # Normal behaviour for a new block
        if len(self.chain) > 0:
            block_string = json.dumps(self.last_block, sort_keys=True)

            guess = f"{block_string}{proof}".encode()

            current_hash = hashlib.sha256(guess).hexdigest()
        else:
            # Genesis block only
            current_hash = ""

        # New block
        block = {
            "index": len(self.chain) + 1,
            "hash": current_hash,
            "proof": proof,
            "timestamp": time(),
            "transactions": self.current_transactions,
            "previous_hash": previous_hash or self.hash(self.chain[-1]),
        }

        # Reset current block tx's
        self.current_transactions = []

        # Append new block to chain
        self.chain.append(block)

        # Return new block
        return block

    def hash(self, block):
        """
        Creates a SHA-256 hash of a Block
​
        :param block": <dict> Block
        "return": <str>
        """

        # 1. hashlib requires byte string to hash
        # 2. Must maintain order of hashes

        # Create block string
        string_object = json.dumps(block, sort_keys=True)
        block_string = string_object.encode()

        # Hash block string using sha256
        # hexdigest converts to hex string (easier to work with)
        raw_hash = hashlib.sha256(block_string)
        hex_hash = raw_hash.hexdigest()

        return hex_hash

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self):
        """
        Simple Proof of Work Algorithm
        Stringify the block and look for a proof.
        Loop through possibilities, checking each one against `valid_proof`
        in an effort to find a number that is a valid proof
        :return: A valid proof for the provided block
        """

        block_string = json.dumps(self.last_block, sort_keys=True)
        proof = None

        while not self.valid_proof(block_string, proof):
            proof = random.random()
        return proof

    @staticmethod
    def valid_proof(block_string, proof):
        """
        Validates the Proof:  Does hash(block_string, proof) contain 6
        leading zeroes?  Return true if the proof is valid
        :param block_string: <string> The stringified block to use to
        check in combination with `proof`
        :param proof: <int?> The value that when combined with the
        stringified previous block results in a hash that has the
        correct number of leading zeroes.
        :return: True if the resulting hash is a valid proof, False otherwise
        """

        guess = f"{block_string}{proof}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        return guess_hash[:6] == "000000"
