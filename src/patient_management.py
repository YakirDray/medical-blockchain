from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
import json
import os
from datetime import datetime
import time

class PatientManagement:
    def __init__(self):
        print("מאתחל מערכת ניהול מטופלים...")
        
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
        
        # בדיקת יתרות
        admin_balance = self.w3.eth.get_balance(self.admin_account.address)
        print(f"יתרת המנהל: {self.w3.from_wei(admin_balance, 'ether')} ETH")
    
    async def wait_for_transaction(self, tx_hash, timeout=300):
        """המתנה לאישור טרנזקציה עם timeout"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                receipt = self.w3.eth.get_transaction_receipt(tx_hash)
                if receipt:
                    if receipt['status'] == 1:
                        return receipt
                    else:
                        raise Exception("Transaction failed")
            except Exception as e:
                if "not found" not in str(e):
                    raise
            time.sleep(5)
            print(".", end="", flush=True)
        raise TimeoutError(f"Transaction not mined after {timeout} seconds")
    
    def register_new_patient(self, doctor_private_key, name, age, medical_id):
        """רישום מטופל חדש"""
        try:
            print(f"\nרושם מטופל חדש: {name}")
            
            # יצירת חשבון למטופל
            patient_account = Account.create()
            doctor_account = Account.from_key(doctor_private_key)
            
            print("נוצר חשבון למטופל")
            print(f"כתובת: {patient_account.address}")
            
            # בדיקת יתרת הרופא
            doctor_balance = self.w3.eth.get_balance(doctor_account.address)
            print(f"יתרת הרופא: {self.w3.from_wei(doctor_balance, 'ether')} ETH")
            
            # רישום המטופל בחוזה עם אופטימיזציית גז
            tx = self.contract.functions.registerPatient(
                patient_account.address,
                name,
                age,
                medical_id
            ).build_transaction({
                'from': doctor_account.address,
                'nonce': self.w3.eth.get_transaction_count(doctor_account.address),
                'gas': self.w3.eth.estimate_gas({
                    'from': doctor_account.address,
                    'to': self.contract.address,
                    'data': self.contract.encodeABI(fn_name='registerPatient', args=[patient_account.address, name, age, medical_id])
                }),
                'gasPrice': int(self.w3.eth.gas_price * 1.2)  # 20% יותר גז
            })
            
            # חתימה ושליחה
            signed_tx = self.w3.eth.account.sign_transaction(tx, doctor_private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            print(f"\nטרנזקציה נשלחה, ממתין לאישור...")
            print(f"Hash: {tx_hash.hex()}")
            
            # המתנה לאישור
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt['status'] == 1:
                print("\n✅ המטופל נרשם בהצלחה!")
                result = {
                    'address': patient_account.address,
                    'private_key': patient_account.key.hex(),
                    'tx_hash': receipt['transactionHash'].hex()
                }
                
                self._save_patient_details(result, name, medical_id)
                return result
            else:
                raise Exception("Transaction failed")
            
        except Exception as e:
            print(f"❌ שגיאה ברישום מטופל: {str(e)}")
            return None
    
    def _save_patient_details(self, patient_data, name, medical_id):
        """שמירת פרטי המטופל לקובץ"""
        try:
            filename = 'patients.json'
            patients = {}
            
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    patients = json.load(f)
            
            patients[patient_data['address']] = {
                'name': name,
                'medical_id': medical_id,
                'private_key': patient_data['private_key'],
                'registration_date': datetime.now().isoformat()
            }
            
            with open(filename, 'w') as f:
                json.dump(patients, f, indent=2)
            
            print(f"פרטי המטופל נשמרו בקובץ: {filename}")
            
        except Exception as e:
            print(f"שגיאה בשמירת פרטי המטופל: {str(e)}")
    
    def get_doctor_patients(self, doctor_private_key):
        """קבלת רשימת המטופלים של רופא"""
        try:
            doctor_account = Account.from_key(doctor_private_key)
            patients = self.contract.functions.getDoctorPatients(doctor_account.address).call({
                'from': doctor_account.address
            })
            
            print(f"\nרשימת מטופלים של הרופא {doctor_account.address}:")
            if not patients:
                print("אין מטופלים רשומים")
                return []
            
            for patient_address in patients:
                details = self.contract.functions.getPatientDetails(patient_address).call({
                    'from': doctor_account.address
                })
                print(f"\nמטופל: {details[0]}")
                print(f"גיל: {details[1]}")
                print(f"ת.ז.: {details[2]}")
            
            return patients
            
        except Exception as e:
            print(f"❌ שגיאה בקבלת רשימת מטופלים: {str(e)}")
            return []

def main():
    try:
        system = PatientManagement()
        
        # פרטי הרופא
        doctor_private_key = "0x40c6505d2ca66f08e4812ede73793138b3481a0a1f5f2b663b500750d4285ccb"
        
        # הצגת רשימת מטופלים נוכחית
        print("\nרשימת מטופלים נוכחית:")
        system.get_doctor_patients(doctor_private_key)
        
        # שאלה האם להוסיף מטופל חדש
        add_patient = input("\nהאם להוסיף מטופל חדש? (כן/לא): ")
        
        if add_patient.lower() == 'כן':
            # רישום מטופל חדש
            patient = system.register_new_patient(
                doctor_private_key=doctor_private_key,
                name="ישראל ישראלי",
                age=35,
                medical_id="123456789"
            )
            
            if patient:
                print("\nפרטי המטופל שנרשם:")
                print(f"כתובת: {patient['address']}")
                print(f"מפתח פרטי: {patient['private_key']}")
                print(f"Hash: {patient['tx_hash']}")
                
                # הצגת רשימה מעודכנת
                print("\nרשימת מטופלים מעודכנת:")
                system.get_doctor_patients(doctor_private_key)
        
    except Exception as e:
        print(f"שגיאה בהרצת התוכנית: {str(e)}")

if __name__ == "__main__":
    main()
