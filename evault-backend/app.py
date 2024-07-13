from flask import Flask, request, jsonify
from flask_cors import CORS
from web3 import Web3
import json
import ipfshttpclient
from cryptography.fernet import Fernet
import requests
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
app = Flask(__name__)
CORS(app)

# Connect to the local Ganache blockchain
web3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
# Load contract ABI and address from the saved JSON file
with open('../Contracts/contracts/contract_info.json') as f:
    contract_info = json.load(f)
contract_abi = contract_info['abi']
contract_address = contract_info['address']

contract = web3.eth.contract(address=contract_address, abi=contract_abi)

password = b"SGRxHarish"
salt = os.urandom(16)
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=390000,
)
key = base64.urlsafe_b64encode(kdf.derive(password))
print(key)
cipher_suite = Fernet(key)
# IPFS API URL
ipfs_api_url = 'http://127.0.0.1:5001/api/v0'

@app.route('/upload', methods=['POST'])
def upload_document():
    try:
        # Check if file and title are in the request
        print("Received request")
        print("Request method:", request.method)
        print("Request headers:", request.headers)
        print("Request files:", request.files)
        print("Request form data:", request.form)
        if 'file' not in request.files:
            return jsonify({'error': 'File is required'}), 400
        if 'title' not in request.form:
            return jsonify({'error': 'Title is required'}), 400

        file = request.files['file']
        title = request.form['title']

        print(f"Received file: {file.filename}")
        print(f"Received title: {title}")

        # Upload file to IPFS
        files = {'file': file.read()}
        
        response = requests.post(f'{ipfs_api_url}/add', files=files)
        response.raise_for_status()  # Check for HTTP request errors
        ipfs_hash = response.json()['Hash']

        
        print(f" IPFS Hash: {ipfs_hash}")
        # Call smart contract function to store the IPFS hash
        # tx_hash = contract.functions.createRecord(ipfs_hash, title).transact({'from': web3.eth.accounts[0]})
        tx_hash = contract.functions.createRecord(ipfs_hash, title).transact({'from': web3.eth.accounts[0]})
        
        return jsonify({'tx_hash': tx_hash.hex(), 'ipfs_hash': ipfs_hash}), 201
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/update/<int:record_id>', methods=['POST'])
def update_document(record_id):
    try:
        file = request.files['file']
        title = request.form['title']

        # Upload file to IPFS
        files = {'file': file.read()}
        response = requests.post(f'{ipfs_api_url}/add', files=files)
        ipfs_hash = response.json()['Hash']

        # Call smart contract function to update the IPFS hash
        tx_hash = contract.functions.updateRecord(record_id, ipfs_hash, title).transact({'from': web3.eth.accounts[0]})

        return jsonify({'tx_hash': tx_hash.hex(), 'ipfs_hash': ipfs_hash}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/log_activity/<int:record_id>', methods=['POST'])
def log_activity(record_id):
    try:
        action = request.form['action']
        tx_hash = contract.functions.logActivity(record_id, action).transact({'from': web3.eth.accounts[0]})
        return jsonify({'tx_hash': tx_hash.hex()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_record/<int:record_id>', methods=['GET'])
def get_record(record_id):
    try:
        record = contract.functions.getRecord(record_id).call()
        return jsonify({'id': record[0], 'ipfs_hash': record[1], 'title': record[2], 'owner': record[3]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_all_records', methods=['GET'])
def get_all_records():
    try:
        records = contract.functions.getAllRecords().call()
        # Decrypt the IPFS hash
        all_records = [
            {'id': record[0], 'ipfs_hash': record[1], 'title': record[2], 'owner': record[3]}
            for record in records
        ]
        return jsonify(all_records), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_activities/<int:record_id>', methods=['GET'])
def get_activities(record_id):
    try:
        activities = contract.functions.getActivities(record_id).call()
        all_activities = [
            {'recordId': activity[0], 'action': activity[1], 'user': activity[2], 'timestamp': activity[3]}
            for activity in activities
        ]
        return jsonify(all_activities), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)