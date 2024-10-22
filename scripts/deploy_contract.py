from web3 import Web3
from eth_account import Account
import json
import os
from dotenv import load_dotenv
from pathlib import Path
import time

def deploy_contract():
    print("מתחיל תהליך התקנת החוזה עם הגדרות גז מעודכנות...\n")
    
    try:
        # טעינת משתני סביבה
        load_dotenv()
        provider_url = os.getenv('PROVIDER_URL')
        private_key = os.getenv('ADMIN_PRIVATE_KEY')
        
        # התחברות לרשת
        print("מתחבר לרשת...")
        w3 = Web3(Web3.HTTPProvider(provider_url))
        
        # טעינת החשבון
        account = Account.from_key(private_key)
        print(f"משתמש בחשבון: {account.address}")
        
        # בדיקת יתרה
        balance = w3.eth.get_balance(account.address)
        balance_eth = w3.from_wei(balance, 'ether')
        print(f"יתרה נוכחית: {balance_eth} ETH")
        
        # טעינת החוזה המקומפל
        with open('build/MedicalRegistry.json', 'r') as file:
            contract_json = json.load(file)
            
        # הכנת החוזה להתקנה
        contract_interface = contract_json['contracts']['MedicalRegistry.sol']['MedicalRegistry']
        abi = contract_interface['abi']
        bytecode = contract_interface['evm']['bytecode']['object']
        
        print("\nמכין את החוזה להתקנה...")
        MedicalRegistry = w3.eth.contract(abi=abi, bytecode=bytecode)
        
        # חישוב הערכת גז
        gas_estimate = w3.eth.estimate_gas({
            'from': account.address,
            'data': bytecode
        })
        
        gas_with_buffer = int(gas_estimate * 1.2)  # הוספת 20% באפר
        print(f"הערכת גז: {gas_estimate}")
        print(f"גז עם באפר: {gas_with_buffer}")
        
        # קבלת מחיר גז נוכחי
        gas_price = w3.eth.gas_price
        gas_price_gwei = w3.from_wei(gas_price, 'gwei')
        print(f"מחיר גז נוכחי: {gas_price_gwei} Gwei")
        
        # חישוב עלות משוערת
        estimated_cost = w3.from_wei(gas_price * gas_with_buffer, 'ether')
        print(f"עלות משוערת: {estimated_cost} ETH")
        
        if balance < (gas_price * gas_with_buffer):
            raise ValueError(f"אין מספיק ETH! נדרש: {estimated_cost} ETH")
        
        # בניית טרנזקצית ההתקנה
        print("\nבונה טרנזקציה...")
        transaction = MedicalRegistry.constructor().build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': gas_with_buffer,
            'gasPrice': gas_price
        })
        
        # חתימה ושליחה
        print("חותם ושולח את הטרנזקציה...")
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        print(f"\nטרנזקציה נשלחה! מחכה לאישור...")
        print(f"Hash: {tx_hash.hex()}")
        
        # המתנה לאישור
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if tx_receipt['status'] == 1:
            contract_address = tx_receipt['contractAddress']
            print(f"\n✅ החוזה הותקן בהצלחה!")
            print(f"כתובת החוזה: {contract_address}")
            
            # שמירת כתובת החוזה
            with open('.env', 'a') as f:
                f.write(f'\nCONTRACT_ADDRESS={contract_address}')
                
            return contract_address
        else:
            raise Exception("התקנת החוזה נכשלה")
            
    except Exception as e:
        print(f"\n❌ שגיאה בהתקנה: {str(e)}")
        return None

if __name__ == "__main__":
    deploy_contract()