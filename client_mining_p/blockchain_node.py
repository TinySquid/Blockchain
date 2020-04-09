import hashlib
import json

from time import time

from uuid import uuid4
from flask import Flask, jsonify, request

from blockchain import Blockchain

# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace("-", "")

# Instantiate the Blockchain
blockchain = Blockchain(difficulty=4)


@app.route("/mine", methods=["POST"])
def mine():
    try:
        data = request.get_json()
    except:
        # TODO Handle bad requests
        print("Invalid request body")

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

        valid_proof = (
            proof_hash[: blockchain.difficulty] == blockchain.difficulty_string
        )

        if valid_proof:
            # Create miner reward tx
            blockchain.new_transaction("0", data["id"], blockchain.reward)

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
        else:
            response = {"success": False}

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
    # Last block in chain
    block = blockchain.chain[-1]

    # TODO Needs a re-work
    # Target time per block in seconds
    target_time = 60
    # Margin buffer time in percent
    time_margin = 0.35
    # Sample last n blocks
    target_blocks = 10
    # Last n blocks
    last_n_blocks = blockchain.chain[-target_blocks:]
    # Last n blocks time
    last_n_time = 0

    if len(last_n_blocks) == target_blocks:
        # Recalculate difficulty
        for i in range(1, len(last_n_blocks)):
            current_block = last_n_blocks[i]
            prev_block = last_n_blocks[i - 1]
            last_n_time += current_block["timestamp"] - prev_block["timestamp"]

        # Get average time per block
        average_time = last_n_time / target_blocks

        # Determine if we need to raise or lower difficulty
        # print(f"Stay under {target_time - (time_margin * target_time)}")
        # print(f"Stay above {target_time + (time_margin * target_time)}")
        # print(f"Actual {average_time}")
        if average_time < target_time - (time_margin * target_time):
            new_difficulty = blockchain.difficulty + 1
        elif average_time > target_time + (time_margin * target_time):
            new_difficulty = blockchain.difficulty - 1

        # Prevent less than 1 difficulty if necessary
        if new_difficulty < 4:
            new_difficulty = 4

        # Update difficulty
        blockchain.update_difficulty(new_difficulty)

    response = {
        "block": {
            "index": block["index"],
            "transactions": block["transactions"],
            "proof": block["proof"],
            "previous_hash": block["previous_hash"],
            "hash": block["hash"],
            "timestamp": block["timestamp"],
        },
        "difficulty": blockchain.difficulty,
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
    app.run(host="0.0.0.0", port=5000, debug=True)
