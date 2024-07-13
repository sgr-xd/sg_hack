from flask import Flask, request, jsonify, send_file, session
from flask_cors import CORS
from web3 import Web3
import json
from datetime import datetime,timezone
import io
import requests
import base64
import os
from cryptography.fernet import Fernet
from pymongo import MongoClient
from pymongo.errors import ConfigurationError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Connect to the local Ganache blockchain
web3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))

# Load contract ABI and address from the saved JSON file
with open('../Contracts/contracts/contract_info.json') as f:
    contract_info = json.load(f)
contract_abi = contract_info['abi']
contract_address = contract_info['address']
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Connection with MongoDB
try:
    client = MongoClient('mongodb+srv://sghack:sghack@sg-hack.8a7arb2.mongodb.net/')
    client.admin.command('ping')
    print("Connected to MongoDB")
    db = client['eVault'] 
    user_collection = db['users']
except (ConnectionError, ConfigurationError) as e:
    print(f"Failed to connect to MongoDB: {e}")

# Create default admin user if not exists
try:
    if user_collection.count_documents({'username': 'admin'}) == 0:
                 
        cipher_key = base64.urlsafe_b64encode(os.urandom(32))
        admin_user = {
            'username': 'admin',
            'password': generate_password_hash('admin'),
            'user_type': 'Admin',
            'cipher_key': cipher_key
        }
        user_collection.insert_one(admin_user)
        print("Default admin user created.")
except Exception as e:
    print(jsonify({'error': str(e)}), 500)




# IPFS API URL
ipfs_api_url = 'http://127.0.0.1:5001/api/v0'

# Global variable to store user role
user_role = None

# Document Related APIs
@app.route('/upload', methods=['POST'])
def upload_document():
    global user_role
    global user_name
    try:
        role=user_role
        if 'file' not in request.files:
            return jsonify({'error': 'File is required'}), 400
        if 'title' not in request.form:
            return jsonify({'error': 'Title is required'}), 400

        file = request.files['file']
        title = request.form['title']
        user = user_collection.find_one({'username': user_name})
        cipher_key=user['cipher_key']
        print(cipher_key)
        cipher = Fernet(cipher_key)
        encrypted_file = cipher.encrypt(file.read())
        files = {'file': encrypted_file}
        response = requests.post(f'{ipfs_api_url}/add', files=files)
        response.raise_for_status()
        ipfs_hash = response.json()['Hash']

        tx_hash = contract.functions.createRecord(user_role, ipfs_hash, title).transact({'from': web3.eth.accounts[0]})
        record_id = contract.functions.recordCount().call()  # Get the new record ID
       
        # Store record ID in user collection if not Admin
        if user_role != "Admin":
            user_collection.update_one(
                {'username': user_name},
                {'$push': {'records': record_id}}
            )
        return jsonify({'tx_hash': tx_hash.hex(), 'ipfs_hash': ipfs_hash}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/update/<int:record_id>', methods=['POST'])
def update_document(record_id):
    global user_role
    global user_name
    try:
        file = request.files['file']
        title = request.form['title']
        user = user_collection.find_one({'username': user_name})
        cipher_key=user['cipher_key']
        encrypted_file = cipher_key.encrypt(file.read())
        files = {'file': encrypted_file}
        response = requests.post(f'{ipfs_api_url}/add', files=files)
        ipfs_hash = response.json()['Hash']
        role=user_role

        tx_hash = contract.functions.updateRecord(role, record_id, ipfs_hash, title).transact({'from': web3.eth.accounts[0], 'gas': 2000000})

        return jsonify({'tx_hash': tx_hash.hex(), 'ipfs_hash': ipfs_hash}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/delete/<int:record_id>', methods=['POST'])
def delete_document(record_id):
    global user_role
    try:
        role = user_role
        # Call smart contract function to delete the record
        tx_hash = contract.functions.deleteRecord(role, record_id).transact({'from': web3.eth.accounts[0], 'gas': 2000000})
        return jsonify({'tx_hash': tx_hash.hex()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_record/<int:record_id>', methods=['GET'])
def get_record(record_id):
    global user_role
    try:
        role=user_role
        record = contract.functions.getRecord(role, record_id).call()
        return jsonify({'id': record[0], 'ipfs_hash': record[1], 'title': record[2], 'owner': record[3]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_all_records', methods=['GET'])
def get_all_records():
    global user_role
    try:
        role = user_role
        records = contract.functions.getAllRecords(role).call()
        all_records = [{'id': record[0], 'ipfs_hash': record[1], 'title': record[2], 'owner': record[3]} for record in records]
        return jsonify(all_records), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_activities/<int:record_id>', methods=['GET'])
def get_activities(record_id):
    global user_role
    try:
        role = user_role
        activities = contract.functions.getActivities(role, record_id).call()
        all_activities = [{'recordId': activity[0], 'ipfsHash': activity[1], 'action': activity[2], 'user': activity[3], 'timestamp': activity[4]} for activity in activities]
        return jsonify(all_activities), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<int:record_id>', methods=['GET'])
def download_document(record_id):
    global user_role
    try:
        record = contract.functions.getRecord(user_role, record_id).call()
        ipfs_hash = record[1]

        response = requests.post(f'{ipfs_api_url}/cat?arg={ipfs_hash}')
        response.raise_for_status()
        encrypted_file = response.content

        decrypted_file = cipher.decrypt(encrypted_file)

        return send_file(io.BytesIO(decrypted_file),
                         download_name=f'document_{record_id}.pdf',
                         as_attachment=True,
                         mimetype='application/pdf')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_recordIds', methods=['GET'])
def get_record_ids():
    global user_name
    try:
        # Fetch user document from the database
        user = user_collection.find_one({'username': user_name})
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Retrieve the record array
        record_ids = user.get('record', [])
        return jsonify({'record_ids': record_ids}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# User Related APIs
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user_type = data.get('user_type')

    if not username or not password or not user_type:
        print('error'+'Please provide all required fields')
        return jsonify({'error': 'Please provide all required fields'}), 400

    if user_collection.find_one({'username': username}):
        print('error'+'User already exists')
        return jsonify({'error': 'User already exists'}), 400

    hashed_password = generate_password_hash(password)

    cipher_key = base64.urlsafe_b64encode(os.urandom(32))
    
    new_user = {
        'username': username,
        'password': hashed_password,
        'user_type': user_type,
        'cipher_key': cipher_key,
        'record': []
    }

    user_collection.insert_one(new_user)

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    global user_role
    global user_name
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Please provide all required fields'}), 400

    user = user_collection.find_one({'username': username})
    if user and check_password_hash(user['password'], password):
        session['username'] = username
        session['user_type'] = user['user_type']
        user_role = user['user_type']
        user_name=username
        return jsonify({'message': 'Login successful', 'user_type': user['user_type']}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/logout', methods=['POST'])
def logout():
    global user_role
    session.pop('username', None)
    session.pop('user_type', None)
    user_role = None
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/admin/users', methods=['GET'])
def list_users():
    users = user_collection.find()
    user_list = [{'username': user['username'], 'user_type': user['user_type']} for user in users]
    return jsonify(user_list), 200

@app.route('/generate_log', methods=['GET'])
def generate_log():
    global user_role
    try:
        role = user_role
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
                timestamp = datetime.fromtimestamp(entry['timestamp'], tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                log_file.write(f"Record ID: {entry['record_id']}, IPFS Hash: {entry['ipfsHash']}, Action: {entry['action']}, User: {entry['user']}, Timestamp: {timestamp}\n")

        return send_file(log_file_path, as_attachment=True)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
