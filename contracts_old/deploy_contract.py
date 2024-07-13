from web3 import Web3
import json

# Connect to the local Ganache blockchain
web3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

# Set the default account (ensure this account has Ether for gas fees)
web3.eth.default_account = web3.eth.accounts[0]

# Load the compiled contract's ABI and bytecode
with open('build/eVault.abi', 'r') as abi_file:
    contract_abi = json.load(abi_file)

with open('build/eVault.bin', 'r') as bin_file:
    contract_bytecode = bin_file.read()

# Deploy the contract
eVault = web3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)
tx_hash = eVault.constructor().transact()
tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

# Get the contract address
contract_address = tx_receipt.contractAddress

print(f"Contract deployed at address: {contract_address}")

# Save the contract ABI and address for later use
with open('contract_info.json', 'w') as f:
    json.dump({'abi': contract_abi, 'address': contract_address}, f)
