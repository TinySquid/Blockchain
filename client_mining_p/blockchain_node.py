from uuid import uuid4

from flask import Flask, jsonify, request

from blockchain import Blockchain

# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace("-", "")

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route("/mine", methods=["GET"])
def mine():
    # Run the proof of work algorithm to get the next proof
    proof = blockchain.proof_of_work()

    # Forge the new Block by adding it to the chain with the proof
    previous_hash = blockchain.hash(blockchain.last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        "message": "New block found!",
        "index": block["index"],
        "transactions": block["transactions"],
        "proof": block["proof"],
        "previous_hash": previous_hash,
        "hash": block["hash"],
    }

    return jsonify(response), 200


@app.route("/chain", methods=["GET"])
def full_chain():
    response = {
        "length": len(blockchain.chain),
        "chain": blockchain.chain,
    }
    return jsonify(response), 200


@app.route("/last_block", methods=["GET"])
def last_block():
    block = blockchain.chain[-1]
    response = {
        "index": block["index"],
        "transactions": block["transactions"],
        "proof": block["proof"],
        "previous_hash": block["previous_hash"],
        "hash": block["hash"],
        "timestamp": block["timestamp"],
    }
    return jsonify(response), 200


# Run the program on port 5000
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
