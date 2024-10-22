try:
    from web3 import Web3
    from eth_account.account import Account
    from dotenv import load_dotenv
    import os
    print("כל החבילות נטענו בהצלחה!")
except ImportError as e:
    print(f"שגיאה בטעינת חבילה: {str(e)}")
    exit(1)

def check_deployment_prerequisites():
    try:
        # טעינת משתני סביבה
        load_dotenv()
        
        # הדפסת משתני הסביבה (ללא המפתח הפרטי)
        print("\nמשתני סביבה שנטענו:")
        env_vars = {k: v for k, v in os.environ.items() if 'PROVIDER' in k or 'INFURA' in k}
        for key, value in env_vars.items():
            print(f"{key}: {value}")
        
        # התחברות לרשת
        provider_url = os.getenv('PROVIDER_URL')
        if not provider_url:
            raise ValueError("PROVIDER_URL לא נמצא בקובץ .env")
            
        print(f"\nמתחבר ל: {provider_url}")
        w3 = Web3(Web3.HTTPProvider(provider_url))
        
        if not w3.is_connected():
            raise ConnectionError("לא מצליח להתחבר לרשת")
        
        print("התחבר בהצלחה לרשת!")
        
        # בדיקת חשבון המנהל
        admin_private_key = os.getenv('ADMIN_PRIVATE_KEY')
        if not admin_private_key:
            raise ValueError("ADMIN_PRIVATE_KEY לא נמצא בקובץ .env")
            
        if not admin_private_key.startswith('0x'):
            admin_private_key = '0x' + admin_private_key
            
        admin_account = Account.from_key(admin_private_key)
        balance = w3.eth.get_balance(admin_account.address)
        balance_eth = w3.from_wei(balance, 'ether')
        
        print("\nפרטי החשבון:")
        print(f"כתובת: {admin_account.address}")
        print(f"יתרה: {balance_eth} ETH")
        
        # בדיקת החיבור לרשת
        print(f"\nפרטי הרשת:")
        print(f"Chain ID: {w3.eth.chain_id}")
        print(f"Latest Block: {w3.eth.block_number}")
        
        return True
        
    except Exception as e:
        print(f"\nשגיאה: {str(e)}")
        return False

if __name__ == "__main__":
    print("מתחיל בדיקת דרישות מוקדמות...")
    check_deployment_prerequisites()