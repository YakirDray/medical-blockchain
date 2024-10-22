from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
import os

class AccountFunder:
    def __init__(self):
        load_dotenv()
        self.w3 = Web3(Web3.HTTPProvider(os.getenv('PROVIDER_URL')))
        self.admin_account = Account.from_key(os.getenv('ADMIN_PRIVATE_KEY'))
        
        admin_balance = self.w3.eth.get_balance(self.admin_account.address)
        print(f"יתרת מנהל: {self.w3.from_wei(admin_balance, 'ether')} ETH")
    
    def fund_account(self, address, amount_in_eth):
        """העברת ETH לחשבון"""
        try:
            print(f"\nמעביר {amount_in_eth} ETH לכתובת: {address}")
            
            # בדיקת יתרה נוכחית
            current_balance = self.w3.eth.get_balance(address)
            print(f"יתרה נוכחית: {self.w3.from_wei(current_balance, 'ether')} ETH")
            
            # העברת ETH
            tx = {
                'from': self.admin_account.address,
                'to': address,
                'value': self.w3.to_wei(amount_in_eth, 'ether'),
                'nonce': self.w3.eth.get_transaction_count(self.admin_account.address),
                'gas': 21000,
                'gasPrice': self.w3.eth.gas_price
            }
            
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.admin_account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            print("ממתין לאישור ההעברה...")
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # בדיקת יתרה חדשה
            new_balance = self.w3.eth.get_balance(address)
            print(f"✅ ההעברה הושלמה!")
            print(f"יתרה חדשה: {self.w3.from_wei(new_balance, 'ether')} ETH")
            print(f"Hash: {receipt['transactionHash'].hex()}")
            
            return True
            
        except Exception as e:
            print(f"❌ שגיאה בהעברת כספים: {str(e)}")
            return False

def main():
    funder = AccountFunder()
    
    # כתובת הרופא שרשמנו
    doctor_address = "0xc96E471f4ab8900D5BB4BCc7362D126B7eF235a0"
    
    # העברת ETH לרופא
    funder.fund_account(doctor_address, 0.05)

if __name__ == "__main__":
    main()