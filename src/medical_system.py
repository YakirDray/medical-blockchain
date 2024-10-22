from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
from hexbytes import HexBytes
import json
import os
from datetime import datetime

class MedicalSystem:
    def __init__(self):
        print("מאתחל מערכת רפואית...")
        self.load_environment()
        self.connect_to_blockchain()
        self.load_contract()
    
    def load_environment(self):
        """טעינת משתני סביבה"""
        from dotenv import load_dotenv
        load_dotenv()
        
        self.provider_url = os.getenv('PROVIDER_URL')
        self.admin_private_key = os.getenv('ADMIN_PRIVATE_KEY')
        if self.admin_private_key and not self.admin_private_key.startswith('0x'):
            self.admin_private_key = '0x' + self.admin_private_key
        self.contract_address = os.getenv('CONTRACT_ADDRESS')
        
        if not all([self.provider_url, self.admin_private_key, self.contract_address]):
            raise ValueError("חסרים משתני סביבה נדרשים")
    
    def connect_to_blockchain(self):
        """התחברות לבלוקצ'יין"""
        self.w3 = Web3(Web3.HTTPProvider(self.provider_url))
        if not self.w3.is_connected():
            raise ConnectionError("לא ניתן להתחבר לבלוקצ'יין")
        
        try:
            self.admin_account = self.w3.eth.account.from_key(self.admin_private_key)
            print(f"חשבון מנהל: {self.admin_account.address}")
            
            # בדיקת יתרה
            balance = self.w3.eth.get_balance(self.admin_account.address)
            print(f"יתרת ETH: {self.w3.from_wei(balance, 'ether')}")
            
        except Exception as e:
            raise Exception(f"שגיאה בטעינת חשבון: {str(e)}")
    
    def send_transaction(self, transaction_dict, private_key):
        """שליחת טרנזקציה"""
        try:
            # חתימה על הטרנזקציה
            signed = self.w3.eth.account.sign_transaction(
                transaction_dict,
                private_key=private_key
            )
            
            # שליחת הטרנזקציה החתומה
            tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
            print(f"ממתין לאישור טרנזקציה {tx_hash.hex()}...")
            
            # המתנה לאישור
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return receipt
            
        except Exception as e:
            print(f"שגיאה בשליחת טרנזקציה: {str(e)}")
            raise
    
    def register_doctor(self, name, specialization, license_number, email):
        """רישום רופא חדש"""
        try:
            print(f"\nמתחיל רישום רופא: {name}")
            
            # יצירת חשבון חדש לרופא
            doctor_account = self.w3.eth.account.create()
            print(f"נוצר חשבון חדש: {doctor_account.address}")
            
            # העברת ETH ראשוני
            print("\nמעביר ETH ראשוני...")
            
            eth_transfer_tx = {
                'nonce': self.w3.eth.get_transaction_count(self.admin_account.address),
                'gasPrice': self.w3.eth.gas_price,
                'gas': 21000,
                'to': doctor_account.address,
                'value': self.w3.to_wei(0.0005, 'ether'),
                'data': b'',
                'chainId': self.w3.eth.chain_id
            }
            
            transfer_receipt = self.send_transaction(eth_transfer_tx, self.admin_private_key)
            if not transfer_receipt.status:
                raise Exception("העברת ETH נכשלה")
            
            print("ETH הועבר בהצלחה!")
            
            # רישום הרופא בחוזה
            print("\nרושם את הרופא בחוזה...")
            
            contract_tx = self.contract.functions.registerDoctor(
                doctor_account.address,
                name,
                specialization,
                license_number,
                email
            ).build_transaction({
                'from': self.admin_account.address,
                'nonce': self.w3.eth.get_transaction_count(self.admin_account.address),
                'gas': 25000,
                'gasPrice': self.w3.eth.gas_price,
                'chainId': self.w3.eth.chain_id
            })
            
            contract_receipt = self.send_transaction(contract_tx, self.admin_private_key)
            if not contract_receipt.status:
                raise Exception("רישום הרופא בחוזה נכשל")
            
            # שמירת פרטי הרופא
            doctor_data = {
                doctor_account.address: {
                    'name': name,
                    'specialization': specialization,
                    'license_number': license_number,
                    'email': email,
                    'private_key': doctor_account.key.hex(),
                    'registration_date': datetime.now().isoformat(),
                    'is_approved': False
                }
            }
            
            self._save_to_json(doctor_data, 'doctors.json')
            print("\nפרטי הרופא נשמרו בהצלחה!")
            
            result = {
                'address': doctor_account.address,
                'private_key': doctor_account.key.hex(),
                'transaction_hash': contract_receipt['transactionHash'].hex()
            }
            
            print("\n✅ הרופא נרשם בהצלחה!")
            return result
            
        except Exception as e:
            print(f"❌ שגיאה ברישום רופא: {str(e)}")
            raise
    
    def _save_to_json(self, new_data, filename):
        """שמירת נתונים לקובץ JSON"""
        try:
            data = {}
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    data = json.load(f)
            
            data.update(new_data)
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"שגיאה בשמירת נתונים: {str(e)}")
            raise
            
    def load_contract(self):
        """טעינת החוזה החכם"""
        try:
            with open('build/contract_abi.json', 'r') as f:
                contract_abi = json.load(f)
            
            self.contract = self.w3.eth.contract(
                address=self.w3.to_checksum_address(self.contract_address),
                abi=contract_abi
            )
            print(f"החוזה נטען בהצלחה!")
            
        except Exception as e:
            raise Exception(f"שגיאה בטעינת החוזה: {str(e)}")