import hashlib
import json

from uuid import uuid4
from flask import Flask, jsonify, request

from blockchain import Blockchain

# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace("-", "")

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route("/mine", methods=["POST"])
def mine():
    data = request.get_json()

    if "id" not in data or "proof" not in data:
        # Bad Request
        return jsonify({"error": "Request missing an id and/or a proof"}), 400
    else:
        # Check if proof is unique to chain
        for block in blockchain.chain:
            if block["proof"] == data["proof"]:
                # Proof already submitted previously
                return jsonify({"success": False})

        # Validate proof
        block_string = json.dumps(blockchain.last_block, sort_keys=True)
        proof_string = f"{block_string}{data['proof']}".encode()
        proof_hash = hashlib.sha256(proof_string).hexdigest()

        valid_proof = proof_hash[:2] == "00"

        if valid_proof:
            # Create miner reward tx
            blockchain.new_transaction("0", data["id"], 1)

            # Forge the new Block by adding it to the chain with the proof
            previous_hash = blockchain.hash(blockchain.last_block)
            block = blockchain.new_block(data["proof"], previous_hash)

            response = {
                "success": True,
                "message": "New block forged!",
                "index": block["index"],
                "transactions": block["transactions"],
                "proof": block["proof"],
                "previous_hash": previous_hash,
                "hash": block["hash"],
            }

        return jsonify(response)


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


@app.route("/transactions/new", methods=["POST"])
def new_transaction():
    values = request.get_json()

    required = ["sender", "recipient", "amount"]
    if not all(k in values for k in required):
        return jsonify({"error": "Requires sender, recipient, and amount"}), 400

    index = blockchain.new_transaction(
        values["sender"], values["recipient"], values["amount"]
    )

    response = {"message": f"Transaction will be added to Block {index}"}

    return jsonify(response), 200


# Run the program on port 5000
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
