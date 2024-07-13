from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
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

@app.route('/delete/<int:record_id>', methods=['POST'])
def delete_document(record_id):
    try:
        if 'role' not in request.form:
            return jsonify({'error': 'Role is required'}), 400

        role = request.form['role']

        # Call smart contract function to delete the record
        tx_hash = contract.functions.deleteRecord(role, record_id).transact({'from': web3.eth.accounts[0], 'gas': 2000000})
        return jsonify({'tx_hash': tx_hash.hex()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/log_activity/<int:record_id>', methods=['POST'])
def log_activity(record_id):
    try:
        if 'action' not in request.form or 'role' not in request.form or 'ipfsHash' not in request.form:
            return jsonify({'error': 'Action, role, and ipfsHash are required'}), 400

        action = request.form['action']
        role = request.form['role']
        ipfs_hash = request.form['ipfsHash']
        tx_hash = contract.functions.logActivity(role, record_id, ipfs_hash, action).transact({'from': web3.eth.accounts[0], 'gas': 2000000})
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
        all_activities = [{'recordId': activity[0], 'ipfsHash': activity[1], 'action': activity[2], 'user': activity[3], 'timestamp': activity[4]} for activity in activities]
        return jsonify(all_activities), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_log', methods=['GET'])
def generate_log():
    try:
        role = request.args.get('role')
        records = contract.functions.getAllRecords(role).call()
        log_entries = []

        for record in records:
            record_id = record[0]
            activities = contract.functions.getActivities(role, record_id).call()
            for activity in activities:
                log_entries.append({
                    'record_id': record_id,
                    'ipfsHash': activity[1],
                    'action': activity[2],
                    'user': activity[3],
                    'timestamp': activity[4]
                })
        log_entries.sort(key=lambda x: x['timestamp'])

        log_file_path = 'activity_log.txt'
        with open(log_file_path, 'w') as log_file:
            for entry in log_entries:
                timestamp = datetime.utcfromtimestamp(entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                log_file.write(f"Record ID: {entry['record_id']}, IPFS Hash: {entry['ipfsHash']}, Action: {entry['action']}, User: {entry['user']}, Timestamp: {timestamp}\n")

        return send_file(log_file_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
