from flask import Flask, request, jsonify, send_file, session
from flask_cors import CORS
from web3 import Web3
import json
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
        admin_random_key = base64.urlsafe_b64encode(os.urandom(32))
        user_cipher = Fernet(admin_random_key)
        cipher_key = user_cipher.encrypt('admin'.encode())
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

fixed_key = base64.urlsafe_b64encode(os.urandom(32))
cipher = Fernet(fixed_key)

# IPFS API URL
ipfs_api_url = 'http://127.0.0.1:5001/api/v0'

# Global variable to store user role
user_role = None

# Document Related APIs
@app.route('/upload', methods=['POST'])
def upload_document():
    global user_role
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'File is required'}), 400
        if 'title' not in request.form:
            return jsonify({'error': 'Title is required'}), 400

        file = request.files['file']
        title = request.form['title']

        encrypted_file = cipher.encrypt(file.read())
        files = {'file': encrypted_file}
        response = requests.post(f'{ipfs_api_url}/add', files=files)
        response.raise_for_status()
        ipfs_hash = response.json()['Hash']

        tx_hash = contract.functions.createRecord(user_role, ipfs_hash, title).transact({'from': web3.eth.accounts[0]})

        return jsonify({'tx_hash': tx_hash.hex(), 'ipfs_hash': ipfs_hash}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/update/<int:record_id>', methods=['POST'])
def update_document(record_id):
    global user_role
    try:
        file = request.files['file']
        title = request.form['title']

        encrypted_file = cipher.encrypt(file.read())
        files = {'file': encrypted_file}
        response = requests.post(f'{ipfs_api_url}/add', files=files)
        ipfs_hash = response.json()['Hash']

        tx_hash = contract.functions.updateRecord(user_role, record_id, ipfs_hash, title).transact({'from': web3.eth.accounts[0]})

        return jsonify({'tx_hash': tx_hash.hex(), 'ipfs_hash': ipfs_hash}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/log_activity/<int:record_id>', methods=['POST'])
def log_activity(record_id):
    global user_role
    try:
        action = request.form['action']
        tx_hash = contract.functions.logActivity(user_role, record_id, action).transact({'from': web3.eth.accounts[0]})
        return jsonify({'tx_hash': tx_hash.hex()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_record/<int:record_id>', methods=['GET'])
def get_record(record_id):
    global user_role
    try:
        record = contract.functions.getRecord(user_role, record_id).call()
        return jsonify({'id': record[0], 'ipfs_hash': record[1], 'title': record[2], 'owner': record[3]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_all_records', methods=['GET'])
def get_all_records():
    global user_role
    try:
        records = contract.functions.getAllRecords(user_role).call()
        all_records = [
            {'id': record[0], 'ipfs_hash': record[1], 'title': record[2], 'owner': record[3]}
            for record in records
        ]
        return jsonify(all_records), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_activities/<int:record_id>', methods=['GET'])
def get_activities(record_id):
    global user_role
    try:
        activities = contract.functions.getActivities(user_role, record_id).call()
        all_activities = [
            {'recordId': activity[0], 'action': activity[1], 'user': activity[2], 'timestamp': activity[3]}
            for activity in activities
        ]
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

@app.route('/delete/<int:record_id>', methods=['DELETE', 'POST'])
def delete_document(record_id):
    global user_role
    try:
        tx_hash = contract.functions.deleteRecord(user_role, record_id).transact({'from': web3.eth.accounts[0]})
        return jsonify({'tx_hash': tx_hash.hex(), 'status': 'Document deleted'}), 200
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
        return jsonify({'error': 'Please provide all required fields'}), 400

    if user_collection.find_one({'username': username}):
        return jsonify({'error': 'User already exists'}), 400

    hashed_password = generate_password_hash(password)

    user_random_key = base64.urlsafe_b64encode(os.urandom(32))
    user_cipher = Fernet(user_random_key)
    cipher_key = user_cipher.encrypt(password.encode())
    
    new_user = {
        'username': username,
        'password': hashed_password,
        'user_type': user_type,
        'cipher_key': cipher_key
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

if __name__ == '__main__':
    app.run(debug=True)
