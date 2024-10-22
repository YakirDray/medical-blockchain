import requests
from datetime import datetime
import time

def check_faucet_availability():
    faucets = [
        {
            'name': 'Infura Sepolia Faucet',
            'url': 'https://www.infura.io/faucet/sepolia',
            'requirements': 'חשבון Infura'
        },
        {
            'name': 'Chainlink Faucet',
            'url': 'https://faucets.chain.link/sepolia',
            'requirements': 'אין דרישות מיוחדות'
        },
        {
            'name': 'RockX Faucet',
            'url': 'https://faucet-sepolia.rockx.com/',
            'requirements': 'אין דרישות מיוחדות'
        }
    ]
    
    print("בודק זמינות של Faucets...\n")
    
    for faucet in faucets:
        print(f"בודק {faucet['name']}:")
        print(f"URL: {faucet['url']}")
        print(f"דרישות: {faucet['requirements']}")
        
        try:
            response = requests.head(faucet['url'], timeout=5)
            if response.status_code == 200:
                print("✅ זמין")
            else:
                print("❌ לא זמין")
        except:
            print("❌ לא ניתן לגשת")
        print()
    
    print("\nהמלצות:")
    print("1. נסה קודם את Infura Faucet אם יש לך חשבון")
    print("2. אם לא, נסה את Chainlink Faucet")
    print("3. אם שניהם לא עובדים, נסה את RockX Faucet")
    
    print("\nכתובת הארנק שלך:")
    print("0x0DC1251C95138622C99B50836BC0e23AfAc14e13")

if __name__ == "__main__":
    check_faucet_availability()