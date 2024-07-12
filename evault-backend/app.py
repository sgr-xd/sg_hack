from flask import Flask, request, jsonify
from flask_cors import CORS
from web3 import Web3
import json
import os
import hashlib

app = Flask(__name__)
CORS(app)

# Connect to the local Ganache blockchain
web3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

# Load contract ABI and address from the saved JSON file
with open('../contracts/contract_info.json') as f:
    contract_info = json.load(f)
contract_abi = contract_info['abi']
contract_address = contract_info['address']

contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Create an uploads directory if it doesn't exist
os.makedirs('uploads', exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_document():
    file = request.files['file']
    title = request.form['title']
    file_path = f"uploads/{file.filename}"
    file.save(file_path)

    # Calculate hash
    with open(file_path, 'rb') as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()

    # Call smart contract function to store the hash
    tx_hash = contract.functions.createRecord(file_hash, title).transact({'from': web3.eth.accounts[0]})

    return jsonify({'tx_hash': tx_hash.hex(), 'file_hash': file_hash}), 201

@app.route('/get_record/<int:record_id>', methods=['GET'])
def get_record(record_id):
    record = contract.functions.getRecord(record_id).call()
    return jsonify({'id': record[0], 'hash': record[1], 'title': record[2], 'owner': record[3]}), 200

@app.route('/get_all_records', methods=['GET'])
def get_all_records():
    records = contract.functions.getAllRecords().call()
    all_records = [
        {'id': record[0], 'hash': record[1], 'title': record[2], 'owner': record[3]}
        for record in records
    ]
    return jsonify(all_records), 200

if __name__ == '__main__':
    app.run(debug=True)
