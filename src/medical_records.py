from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
import json
import os
from datetime import datetime
import time

class MedicalRecordSystem:
    def __init__(self):
        print("מאתחל מערכת רשומות רפואיות...")
        
        # טעינת נתוני מטופלים קיימים
        self.patients = self._load_patients()
        
        # טעינת הגדרות וחיבור לבלוקצ'יין
        load_dotenv()
        self.w3 = Web3(Web3.HTTPProvider(os.getenv('PROVIDER_URL')))
        
        # טעינת החוזה
        with open('build/contract_abi.json', 'r') as f:
            contract_abi = json.load(f)
        
        self.contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(os.getenv('CONTRACT_ADDRESS')),
            abi=contract_abi
        )
    
    def _load_patients(self):
        """טעינת נתוני מטופלים מהקובץ"""
        try:
            if os.path.exists('patients.json'):
                with open('patients.json', 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"שגיאה בטעינת נתוני מטופלים: {str(e)}")
            return {}
    
    def add_medical_record(self, doctor_private_key, patient_address, record_data):
        """הוספת רשומה רפואית"""
        try:
            # וידוא שהמטופל קיים
            if patient_address not in self.patients:
                raise ValueError("מטופל לא קיים במערכת")
            
            patient = self.patients[patient_address]
            
            # שמירת הרשומה
            record = {
                'timestamp': datetime.now().isoformat(),
                'doctor': Account.from_key(doctor_private_key).address,
                'data': record_data
            }
            
            # עדכון קובץ הרשומות
            filename = f'medical_records_{patient["medical_id"]}.json'
            records = []
            
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    records = json.load(f)
            
            records.append(record)
            
            with open(filename, 'w') as f:
                json.dump(records, f, indent=2)
            
            print(f"✅ רשומה רפואית נוספה למטופל {patient['name']}")
            return True
            
        except Exception as e:
            print(f"❌ שגיאה בהוספת רשומה רפואית: {str(e)}")
            return False
    
    def get_patient_records(self, doctor_private_key, patient_address):
        """קבלת רשומות רפואיות של מטופל"""
        try:
            if patient_address not in self.patients:
                raise ValueError("מטופל לא קיים במערכת")
            
            patient = self.patients[patient_address]
            filename = f'medical_records_{patient["medical_id"]}.json'
            
            if not os.path.exists(filename):
                print(f"אין רשומות רפואיות למטופל {patient['name']}")
                return []
            
            with open(filename, 'r') as f:
                records = json.load(f)
            
            print(f"\nרשומות רפואיות של המטופל {patient['name']}:")
            for i, record in enumerate(records, 1):
                print(f"\nרשומה {i}:")
                print(f"תאריך: {record['timestamp']}")
                print(f"רופא: {record['doctor']}")
                print("נתונים:")
                for key, value in record['data'].items():
                    print(f"  {key}: {value}")
            
            return records
            
        except Exception as e:
            print(f"❌ שגיאה בקבלת רשומות רפואיות: {str(e)}")
            return []

def main():
    try:
        system = MedicalRecordSystem()
        
        # פרטי הרופא
        doctor_private_key = "0x40c6505d2ca66f08e4812ede73793138b3481a0a1f5f2b663b500750d4285ccb"
        
        # המטופל שרשמנו קודם
        patient_address = "0xcCd772c4CC5Fbc34fF7f7a53363e2903FD96ef45"
        
        # הצגת רשומות קיימות
        print("\nרשומות קיימות:")
        system.get_patient_records(doctor_private_key, patient_address)
        
        # הוספת רשומה חדשה
        add_record = input("\nהאם להוסיף רשומה רפואית חדשה? (כן/לא): ")
        
        if add_record.lower() == 'כן':
            record_data = {
                'סוג ביקור': 'בדיקה שגרתית',
                'לחץ דם': '120/80',
                'דופק': '72',
                'משקל': '75',
                'הערות': 'המטופל במצב תקין'
            }
            
            if system.add_medical_record(doctor_private_key, patient_address, record_data):
                # הצגת רשומות מעודכנות
                print("\nרשומות מעודכנות:")
                system.get_patient_records(doctor_private_key, patient_address)
        
    except Exception as e:
        print(f"שגיאה בהרצת התוכנית: {str(e)}")

if __name__ == "__main__":
    main()