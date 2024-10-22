from web3 import Web3
import requests

def test_rpc_endpoints():
    # רשימת נקודות קצה לבדיקה
    endpoints = [
        {
            'url': 'https://sepolia.infura.io/v3/32609b92970443b08f4e0a3e97d19dd5',
            'name': 'Infura'
        },
        {
            'url': 'https://rpc.sepolia.org',
            'name': 'Public RPC'
        }
    ]
    
    print("בודק חיבור לנקודות קצה שונות...")
    
    for endpoint in endpoints:
        print(f"\nבודק {endpoint['name']}:")
        try:
            # בדיקת חיבור בסיסית
            w3 = Web3(Web3.HTTPProvider(endpoint['url']))
            if w3.is_connected():
                chain_id = w3.eth.chain_id
                block = w3.eth.block_number
                print(f"✓ החיבור הצליח!")
                print(f"Chain ID: {chain_id}")
                print(f"Block Number: {block}")
            else:
                print("✗ החיבור נכשל")
                
        except Exception as e:
            print(f"✗ שגיאה: {str(e)}")
    
    print("\nבודק חיבור לאינטרנט כללי:")
    try:
        response = requests.get('https://google.com')
        print(f"✓ חיבור לאינטרנט תקין (status code: {response.status_code})")
    except Exception as e:
        print(f"✗ בעיה בחיבור לאינטרנט: {str(e)}")

if __name__ == "__main__":
    test_rpc_endpoints()