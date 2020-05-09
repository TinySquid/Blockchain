import hashlib
import requests
import random

import sys
import json

from time import time


def proof_of_work(block, difficulty):
    """
    Simple Proof of Work Algorithm
    Stringify the block and look for a proof.
    Loop through possibilities, checking each one against `valid_proof`
    in an effort to find a number that is a valid proof
    :return: A valid proof for the provided block
    """
    block_string = json.dumps(block, sort_keys=True)
    proof = None

    while not valid_proof(block_string, proof, difficulty):
        proof = random.random()
    return proof


def valid_proof(block_string, proof, difficulty):
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

    return guess_hash[:difficulty] == "0" * difficulty


if __name__ == "__main__":
    # What is the server address? IE `python3 miner.py https://server.com/api/`
    if len(sys.argv) > 1:
        node = sys.argv[1]
    else:
        node = "http://localhost:5000"

    # Load ID
    f = open("my_id.txt", "r")
    id = f.read()
    print("ID is", id)
    f.close()

    mining_difficulty = None
    coins_mined = 0

    # Run forever until interrupted
    while True:
        r = requests.get(url=node + "/last_block")
        # Handle non-json response
        try:
            data = r.json()
        except ValueError:
            print("Error:  Non-json response")
            print("Response returned:")
            print(r)
            break

        # Grab block data
        last_block = data["block"]
        # Store previous difficulty
        prev_difficulty = mining_difficulty
        # Get new difficulty
        mining_difficulty = data["difficulty"]

        if mining_difficulty != prev_difficulty:
            print(f"Difficulty changed from {prev_difficulty} to {mining_difficulty}")

        start_time = time()
        new_proof = proof_of_work(last_block, mining_difficulty)
        end_time = time()

        print(f"Found hash in {end_time - start_time} seconds")

        # When found, POST it to the server {"proof": new_proof, "id": id}
        post_data = {"proof": new_proof, "id": id}

        # print(post_data)

        r = requests.post(url=node + "/mine", json=post_data)
        data = r.json()
        # print(data)

        if "success" in data:
            if data["success"]:
                coins_mined += 5
                print(data["message"])
                # print("Reward: 5 coins")
                # print(f"Balance: {coins_mined}")
            else:
                print("Proof invalid")
        else:
            print("An error occurred")
