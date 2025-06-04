from web3 import Web3
from eth_account import Account
import json
import os

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))

# Load contract ABI
with open('contracts/PeopleCounter.json') as f:
    contract_json = json.load(f)
    contract_abi = contract_json['abi']

# Contract address (update this after deploying)
CONTRACT_ADDRESS = 'YOUR_CONTRACT_ADDRESS'

# Create contract instance
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)

def add_analysis(people_count, percent_levels, source_type, file_hash):
    """
    Add a new analysis to the blockchain
    """
    try:
        tx_hash = contract.functions.addAnalysis(
            people_count,
            percent_levels,
            source_type,
            file_hash
        ).transact()
        return tx_hash
    except Exception as e:
        print(f"Error adding analysis to blockchain: {e}")
        return None

def get_analysis(index):
    """
    Get analysis data from blockchain
    """
    try:
        analysis = contract.functions.getAnalysis(index).call()
        return analysis
    except Exception as e:
        print(f"Error getting analysis from blockchain: {e}")
        return None

def get_total_analyses():
    """
    Get total number of analyses
    """
    try:
        count = contract.functions.getCount().call()
        return count
    except Exception as e:
        print(f"Error getting total analyses: {e}")
        return 0 