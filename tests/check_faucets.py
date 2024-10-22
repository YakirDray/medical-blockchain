import requests
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
import os

def check_faucet_eligibility():
    load_dotenv()
    
    # התחברות לרשתות
    mainnet_w3 = Web3(Web3.HTTPProvider('https://eth-mainnet.g.alchemy.com/v2/demo'))
    sepolia_w3 = Web3(Web3.HTTPProvider(os.getenv('PROVIDER_URL')))
    
    # קבלת כתובת הארנק
    account = Account.from_key(os.getenv('ADMIN_PRIVATE_KEY'))
    address = account.address
    
    print(f"בודק זכאות לקבלת ETH עבור הכתובת: {address}\n")
    
    # בדיקת יתרה ברשת הראשית
    mainnet_balance = mainnet_w3.eth.get_balance(address)
    mainnet_balance_eth = mainnet_w3.from_wei(mainnet_balance, 'ether')
    
    # בדיקת יתרה ב-Sepolia
    sepolia_balance = sepolia_w3.eth.get_balance(address)
    sepolia_balance_eth = sepolia_w3.from_wei(sepolia_balance, 'ether')
    
    print("יתרות נוכחיות:")
    print(f"Mainnet ETH: {mainnet_balance_eth}")
    print(f"Sepolia ETH: {sepolia_balance_eth}\n")
    
    print("Faucets זמינים:")
    
    if mainnet_balance_eth >= 0.001:
        print("✓ Alchemy Sepolia Faucet - זמין")
    else:
        print("✗ Alchemy Sepolia Faucet - דורש 0.001 ETH ברשת הראשית")
    
    print("✓ Sepolia PoW Faucet - זמין תמיד (דורש כרייה בדפדפן)")
    print("✓ Infura Faucet - זמין עם חשבון Infura")
    print("✓ Discord Faucet - זמין דרך שרת Discord של Ethereum")
    
    print("\nהמלצות:")
    if mainnet_balance_eth < 0.001:
        print("1. השתמש ב-Sepolia PoW Faucet")
        print("   https://sepolia-faucet.pk910.de/")
        print("2. נסה את ה-Faucet של Infura")
        print("   https://www.infura.io/faucet/sepolia")
        print("3. בקש ב-Discord")
        print("   https://discord.gg/ethereum")

if __name__ == "__main__":
    check_faucet_eligibility()