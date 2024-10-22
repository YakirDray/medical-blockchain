from web3 import Web3
from requests.exceptions import RequestException
import requests
import time
from dotenv import load_dotenv
import os

def test_network_connection():
    load_dotenv()
    provider_url = os.getenv('PROVIDER_URL')
    
    print(f"בודק חיבור ל: {provider_url}")
    
    # בדיקת חיבור בסיסית
    try:
        response = requests.get("https://api.infura.io/v1/jsonrpc/sepolia/block/latest", 
                              headers={"Content-Type": "application/json"},
                              timeout=10)
        print(f"\nבדיקת Infura API:")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("החיבור ל-Infura תקין!")
        else:
            print("בעיה בחיבור ל-Infura")
    except Exception as e:
        print(f"שגיאה בבדיקת Infura: {str(e)}")

    # ניסיון חיבור Web3
    try:
        print("\nמנסה להתחבר באמצעות Web3...")
        w3 = Web3(Web3.HTTPProvider(provider_url, request_kwargs={'timeout': 30}))
        
        if w3.is_connected():
            print("החיבור הצליח!")
            chain_id = w3.eth.chain_id
            latest_block = w3.eth.block_number
            print(f"Chain ID: {chain_id}")
            print(f"Latest Block: {latest_block}")
        else:
            print("החיבור נכשל")
            
        # בדיקת חיבור ספציפית ל-Sepolia
        print("\nבודק זיהוי רשת Sepolia...")
        if chain_id == 11155111:
            print("מחובר לרשת Sepolia!")
        else:
            print(f"מחובר לרשת לא נכונה. Chain ID: {chain_id}")
            
    except Exception as e:
        print(f"\nשגיאה בחיבור Web3: {str(e)}")
    
    # בדיקת תצורת הרשת
    print("\nהגדרות רשת נוכחיות:")
    print(f"Provider URL: {provider_url}")
    if 'INFURA_API_KEY' in os.environ:
        print(f"Infura API Key: {os.getenv('INFURA_API_KEY')[:6]}...")
        
    return w3.is_connected() if 'w3' in locals() else False

def suggest_solutions():
    print("\nהמלצות לפתרון:")
    print("1. בדוק שה-API key של Infura תקין ופעיל")
    print("2. נסה להירשם מחדש ל-Infura וליצור API key חדש")
    print("3. בדוק את החיבור לאינטרנט")
    print("4. נסה להשתמש ב-VPN או לשנות רשת")
    print("5. אם הבעיה נמשכת, נסה להשתמש ב-Alchemy במקום Infura:")
    print("   https://www.alchemy.com/")

if __name__ == "__main__":
    print("מתחיל בדיקת חיבור מקיפה...")
    success = test_network_connection()
    if not success:
        suggest_solutions()