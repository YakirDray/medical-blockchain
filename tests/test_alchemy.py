from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
import os
import requests

def test_alchemy_connection():
    # טעינת משתני סביבה
    load_dotenv()
    
    provider_url = os.getenv('PROVIDER_URL')
    print(f"בודק חיבור ל: {provider_url}")
    
    # בדיקת חיבור אינטרנט בסיסית
    try:
        print("\nבודק חיבור אינטרנט...")
        response = requests.get("https://www.google.com", timeout=5)
        print(f"חיבור אינטרנט: תקין (status code: {response.status_code})")
    except Exception as e:
        print(f"בעיית חיבור אינטרנט: {str(e)}")
        return
    
    try:
        # יצירת חיבור Web3
        w3 = Web3(Web3.HTTPProvider(provider_url))
        
        if w3.is_connected():
            print("\nהתחבר בהצלחה!")
            
            # בדיקת רשת
            chain_id = w3.eth.chain_id
            print(f"Chain ID: {chain_id}")
            if chain_id == 11155111:
                print("מחובר לרשת Sepolia!")
            else:
                print("מחובר לרשת לא נכונה!")
            
            # בדיקת חשבון
            admin_private_key = os.getenv('ADMIN_PRIVATE_KEY')
            if admin_private_key:
                account = Account.from_key(admin_private_key)
                balance = w3.eth.get_balance(account.address)
                balance_eth = w3.from_wei(balance, 'ether')
                print(f"\nפרטי חשבון:")
                print(f"כתובת: {account.address}")
                print(f"יתרה: {balance_eth} ETH")
            
            # מידע נוסף
            latest_block = w3.eth.block_number
            gas_price = w3.eth.gas_price
            print(f"\nמידע נוסף:")
            print(f"בלוק נוכחי: {latest_block}")
            print(f"מחיר גז: {w3.from_wei(gas_price, 'gwei')} Gwei")
            
        else:
            print("החיבור נכשל!")
            
    except Exception as e:
        print(f"שגיאה: {str(e)}")

if __name__ == "__main__":
    test_alchemy_connection()