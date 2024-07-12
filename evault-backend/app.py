from flask import Flask, request, jsonify
from flask_cors import CORS
from web3 import Web3
import json
import os
import hashlib
import ipfshttpclient
import requests
from pymongo import MongoClient
from flask_bcrypt import Bcrypt

# Flask
app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)

# Connect to MongoDB
client = MongoClient('mongodb+srv://sghack:sghack@sg-hack.8a7arb2.mongodb.net/')
db = client.eVault
users_collection = db.users

# Create default admin account if it doesn't exist
if not users_collection.find_one({'username': 'admin'}):
    hashed_password = bcrypt.generate_password_hash('admin').decode('utf-8')
    users_collection.insert_one({
        'username': 'admin',
        'password': hashed_password
    })

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



@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if users_collection.find_one({'username': data['username']}):
        return jsonify({'message': 'User already exists'}), 400

    user = {
        'username': data['username'],
        'password': hashlib.sha256(data['password'].encode()).hexdigest(),
        'user_type': data['user_type'],  # Include user type
    }
    users_collection.insert_one(user)
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    user = users_collection.find_one({'username': username})
    if user and bcrypt.check_password_hash(user['password'], password):
        return jsonify({'message': 'Login successful', 'user_id': str(user['_id'])}), 200

    return jsonify({'message': 'Invalid username or password'}), 401

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

        print(f"IPFS Hash: {ipfs_hash}")

        # Call smart contract function to store the IPFS hash
        tx_hash = contract.functions.createRecord(ipfs_hash, title).transact({'from': web3.eth.accounts[0],'gas': 2000000})
        
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

@app.route('/users', methods=['GET'])
def get_users():
    users = users_collection.find()
    user_list = [{'username': user['username'], 'user_type': user['user_type'], '_id': str(user['_id'])} for user in users]
    return jsonify(user_list), 200

if __name__ == '__main__':
    app.run(debug=True)
