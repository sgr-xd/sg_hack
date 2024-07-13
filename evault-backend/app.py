from flask import Flask, request, jsonify
from flask_cors import CORS
from web3 import Web3
import json
import requests

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

# IPFS API URL
ipfs_api_url = 'http://127.0.0.1:5001/api/v0'

@app.route('/upload', methods=['POST'])
def upload_document():
    try:
        if 'file' not in request.files or 'title' not in request.form or 'role' not in request.form:
            return jsonify({'error': 'File, title, and role are required'}), 400

        file = request.files['file']
        title = request.form['title']
        role = request.form['role']

        # Upload file to IPFS
        files = {'file': file.read()}
        response = requests.post(f'{ipfs_api_url}/add', files=files)
        response.raise_for_status()
        ipfs_hash = response.json()['Hash']

        # Call smart contract function to store the IPFS hash
        tx_hash = contract.functions.createRecord(role, ipfs_hash, title).transact({'from': web3.eth.accounts[0], 'gas': 2000000})
        return jsonify({'tx_hash': tx_hash.hex(), 'ipfs_hash': ipfs_hash}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/update/<int:record_id>', methods=['POST'])
def update_document(record_id):
    try:
        if 'file' not in request.files or 'title' not in request.form or 'role' not in request.form:
            return jsonify({'error': 'File, title, and role are required'}), 400

        file = request.files['file']
        title = request.form['title']
        role = request.form['role']

        # Upload file to IPFS
        files = {'file': file.read()}
        response = requests.post(f'{ipfs_api_url}/add', files=files)
        response.raise_for_status()
        ipfs_hash = response.json()['Hash']

        # Call smart contract function to update the IPFS hash
        tx_hash = contract.functions.updateRecord(role, record_id, ipfs_hash, title).transact({'from': web3.eth.accounts[0], 'gas': 2000000})
        return jsonify({'tx_hash': tx_hash.hex(), 'ipfs_hash': ipfs_hash}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/log_activity/<int:record_id>', methods=['POST'])
def log_activity(record_id):
    try:
        if 'action' not in request.form or 'role' not in request.form:
            return jsonify({'error': 'Action and role are required'}), 400

        action = request.form['action']
        role = request.form['role']
        tx_hash = contract.functions.logActivity(role, record_id, action).transact({'from': web3.eth.accounts[0], 'gas': 2000000})
        return jsonify({'tx_hash': tx_hash.hex()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_record/<int:record_id>', methods=['GET'])
def get_record(record_id):
    try:
        role = request.args.get('role')
        record = contract.functions.getRecord(role, record_id).call()
        return jsonify({'id': record[0], 'ipfs_hash': record[1], 'title': record[2], 'owner': record[3]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_all_records', methods=['GET'])
def get_all_records():
    try:
        role = request.args.get('role')
        records = contract.functions.getAllRecords(role).call()
        all_records = [{'id': record[0], 'ipfs_hash': record[1], 'title': record[2], 'owner': record[3]} for record in records]
        return jsonify(all_records), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_activities/<int:record_id>', methods=['GET'])
def get_activities(record_id):
    try:
        role = request.args.get('role')
        activities = contract.functions.getActivities(role, record_id).call()
        all_activities = [{'recordId': activity[0], 'action': activity[1], 'user': activity[2], 'timestamp': activity[3]} for activity in activities]
        return jsonify(all_activities), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
