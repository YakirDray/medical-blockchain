from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
import json
import os
from datetime import datetime
import time

class MedicalOperations:
    def __init__(self):
        print("מאתחל מערכת ניהול רפואי...")
        
        # טעינת הגדרות
        load_dotenv()
        self.w3 = Web3(Web3.HTTPProvider(os.getenv('PROVIDER_URL')))
        self.admin_account = Account.from_key(os.getenv('ADMIN_PRIVATE_KEY'))
        
        # טעינת החוזה
        with open('build/contract_abi.json', 'r') as f:
            contract_abi = json.load(f)
        
        self.contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(os.getenv('CONTRACT_ADDRESS')),
            abi=contract_abi
        )
        
        print(f"מחובר לחוזה בכתובת: {os.getenv('CONTRACT_ADDRESS')}")
        
        # בדיקת יתרת המנהל
        balance = self.w3.eth.get_balance(self.admin_account.address)
        print(f"יתרת המנהל: {self.w3.from_wei(balance, 'ether')} ETH")
    
    def is_admin(self, account_address):
        """בודק אם הכתובת היא של המנהל"""
        return account_address == self.admin_account.address

    def send_transaction(self, transaction, private_key, description=""):
        """שליחת טרנזקציה עם ניסיונות חוזרים"""
        try:
            print(f"\nשולח טרנזקציה{': ' + description if description else ''}")
            
            # הגדרת מחיר הגז אוטומטי
            transaction['gas'] = self.w3.eth.estimate_gas(transaction)
            transaction['gasPrice'] = self.w3.eth.gas_price
            
            # חתימה ושליחה
            signed_tx = self.w3.eth.account.sign_transaction(transaction, private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            print(f"טרנזקציה נשלחה. Hash: {tx_hash.hex()}")
            print("ממתין לאישור (עד 5 דקות)...")
            
            # המתנה לאישור עם timeout ארוך יותר
            start_time = time.time()
            while time.time() - start_time < 300:  # 5 דקות
                try:
                    receipt = self.w3.eth.get_transaction_receipt(tx_hash)
                    if receipt is not None:
                        if receipt['status'] == 1:
                            print("✅ הטרנזקציה אושרה!")
                            return receipt
                        else:
                            raise Exception("הטרנזקציה נכשלה")
                except Exception as e:
                    if "not found" not in str(e):
                        raise
                
                time.sleep(5)
                print(".", end="", flush=True)
            
            raise TimeoutError("תם הזמן המוקצב לאישור הטרנזקציה")
            
        except Exception as e:
            print(f"\n❌ שגיאה בשליחת הטרנזקציה: {str(e)}")
            raise
    
    def approve_doctor(self, doctor_address):
        """אישור רופא במערכת"""
        try:
            # בדיקת בעלות
            if not self.is_admin(self.admin_account.address):
                raise PermissionError("רק מנהל יכול לאשר רופאים")
            
            print(f"\nמאשר רופא בכתובת: {doctor_address}")
            
            # בדיקת פרטי הרופא לפני האישור
            doctor = self.contract.functions.getDoctorDetails(doctor_address).call()
            print(f"פרטי הרופא: שם: {doctor[0]}, התמחות: {doctor[1]}")
            
            if doctor[4]:  # doctor.isApproved
                print("הרופא כבר מאושר במערכת")
                return True
            
            # בניית הטרנזקציה
            tx = self.contract.functions.approveDoctor(doctor_address).build_transaction({
                'from': self.admin_account.address,
                'nonce': self.w3.eth.get_transaction_count(self.admin_account.address)
            })
            
            # שליחת הטרנזקציה
            receipt = self.send_transaction(tx, self.admin_account.key, "אישור רופא")
            return True
            
        except PermissionError as pe:
            print(f"❌ שגיאת הרשאה: {str(pe)}")
        except Exception as e:
            print(f"\n❌ שגיאה באישור הרופא: {str(e)}")
            return False
    
    def check_doctor_status(self, doctor_address):
        """בדיקת סטטוס רופא"""
        try:
            details = self.contract.functions.getDoctorDetails(doctor_address).call()
            print("\nסטטוס רופא: שם: {details[0]}, התמחות: {details[1]}")
            return details[4]  # מחזיר האם מאושר
        except Exception as e:
            print(f"❌ שגיאה בבדיקת סטטוס: {str(e)}")
            return False

    def log_transaction(self, tx_receipt, action):
        """רישום כל טרנזקציה ללוג למעקב"""
        try:
            log_entry = {
                'action': action,
                'transaction_hash': tx_receipt['transactionHash'].hex(),
                'status': 'approved' if tx_receipt['status'] == 1 else 'failed',
                'timestamp': datetime.now().isoformat()
            }
            with open('transaction_log.json', 'a') as log_file:
                json.dump(log_entry, log_file, indent=2)
                log_file.write('\n')
            print("🔍 הטרנזקציה נרשמה בלוג.")
        except Exception as e:
            print(f"❌ שגיאה ברישום לוג: {str(e)}")

def main():
    # אתחול המערכת וביצוע פעולות
    try:
        ops = MedicalOperations()
        
        # כתובת הרופא שרשמנו
        doctor_address = "0xc96E471f4ab8900D5BB4BCc7362D126B7eF235a0"
        
        # בדיקת סטטוס נוכחי
        current_status = ops.check_doctor_status(doctor_address)
        
        if not current_status:
            # אישור הרופא
            if ops.approve_doctor(doctor_address):
                print("\nהרופא אושר בהצלחה! 🎉")
                # בדיקה נוספת שהאישור נקלט
                final_status = ops.check_doctor_status(doctor_address)
                if final_status:
                    print("האישור נקלט במערכת")
            else:
                print("\nנכשל באישור הרופא")
        else:
            print("\nהרופא כבר מאושר במערכת")
            
    except Exception as e:
        print(f"שגיאה בהרצת התוכנית: {str(e)}")

if __name__ == "__main__":
    main()
