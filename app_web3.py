from web3 import Web3
from app_config import Config
from app_fetch import fetch_pol_usd

INFURA_URL = Config.INFURA_URL

PRIVATE_KEY = Config.PRIVATE_KEY
PUBLIC_ADDRESS = Web3().eth.account.from_key(PRIVATE_KEY).address

CONTRACT_ADDRESS = "0xb022A1ECA749525B7c07863AC763ed23AcF599C6"
CONTRACT_ABI = [
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"inputs": [],
		"name": "accumulatedFees",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "txId",
				"type": "uint256"
			},
			{
				"internalType": "address",
				"name": "seller",
				"type": "address"
			}
		],
		"name": "initiateTransaction",
		"outputs": [],
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "txId",
				"type": "uint256"
			}
		],
		"name": "markFailed",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "txId",
				"type": "uint256"
			}
		],
		"name": "markSuccess",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "owner",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "platformFeePercent",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "trades",
		"outputs": [
			{
				"internalType": "address",
				"name": "buyer",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "seller",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "amount",
				"type": "uint256"
			},
			{
				"internalType": "bool",
				"name": "settled",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "to",
				"type": "address"
			}
		],
		"name": "withdrawFees",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	}
]

w3 = Web3(Web3.HTTPProvider(INFURA_URL))

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

# Check if the connection is successful
def is_connected_to_blockchain():
    if w3.is_connected():
        print("Connected to the network")
        return True
    else:
        print("Failed to connect // Unauthorized")
        return False

# Function to get MATIC balance
def get_balance(address):
    if not w3.is_address(address):
        return "Invalid address"
    
    balance_wei = w3.eth.get_balance(address)
    balance_pol = w3.from_wei(balance_wei, 'ether')

    matic_usd = fetch_pol_usd()
    if matic_usd is None:
        return "Failed to fetch MATIC/USD rate"
    print(matic_usd)
    balance_usd = float(balance_pol) * float(matic_usd)
                
    return {
        "pol": float(balance_pol),
        "usd": round(balance_usd, 3)
    }

def mark_success(tx_id):
    nonce = w3.eth.get_transaction_count(PUBLIC_ADDRESS)

    txn = contract.functions.markSuccess(tx_id).build_transaction({
        'from': PUBLIC_ADDRESS,
        'gas': 150000,
        'gasPrice': w3.to_wei('30', 'gwei'),
        'nonce': nonce,
        'chainId': 137
    })

    signed_txn = w3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    return w3.to_hex(tx_hash)

def mark_failed(tx_id):
    nonce = w3.eth.get_transaction_count(PUBLIC_ADDRESS)

    txn = contract.functions.markFailed(tx_id).build_transaction({
        'from': PUBLIC_ADDRESS,
        'gas': 150000,
        'gasPrice': w3.to_wei('30', 'gwei'),
        'nonce': nonce,
        'chainId': 137
    })

    signed_txn = w3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    return w3.to_hex(tx_hash)

def withdraw_fees(to_address):
    nonce = w3.eth.get_transaction_count(PUBLIC_ADDRESS)

    txn = contract.functions.withdrawFees(to_address).build_transaction({
        'from': PUBLIC_ADDRESS,
        'gas': 100000,
        'gasPrice': w3.to_wei('30', 'gwei'),
        'nonce': nonce,
        'chainId': 137
    })

    signed_txn = w3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    return w3.to_hex(tx_hash)

is_connected_to_blockchain()