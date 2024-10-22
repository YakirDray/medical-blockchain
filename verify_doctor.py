from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
import json
import os
from datetime import datetime

def verify_doctor_registration():
    print("בודק רישום רופא...\n")
    
    # טעינת הגדרות
    load_dotenv()
    w3 = Web3(Web3.HTTPProvider(os.getenv('PROVIDER_URL')))
    
    # טעינת החוזה
    with open('build/contract_abi.json', 'r') as f:
        contract_abi = json.load(f)
    
    contract = w3.eth.contract(
        address=w3.to_checksum_address(os.getenv('CONTRACT_ADDRESS')),
        abi=contract_abi
    )
    
    # כתובת הרופא שנרשם
    doctor_address = "0xc96E471f4ab8900D5BB4BCc7362D126B7eF235a0"
    
    try:
        # קבלת פרטי הרופא
        details = contract.functions.getDoctorDetails(doctor_address).call()
        
        print("פרטי הרופא שנרשם:")
        print(f"שם: {details[0]}")
        print(f"התמחות: {details[1]}")
        print(f"מספר רישיון: {details[2]}")
        print(f"רשום: {'כן' if details[3] else 'לא'}")
        print(f"מאושר: {'כן' if details[4] else 'לא'}")
        print(f"מספר מטופלים: {details[5]}")
        print(f"אימייל: {details[6]}")
        print(f"תאריך רישום: {datetime.fromtimestamp(details[7])}")
        
        return True
        
    except Exception as e:
        print(f"שגיאה בבדיקת פרטי הרופא: {str(e)}")
        return False

def main():
    if verify_doctor_registration():
        print("\nהרופא נרשם בהצלחה במערכת! 🎉")
        print("\nהמלצות להמשך:")
        print("1. לאשר את הרופא במערכת")
        print("2. להתחיל ברישום מטופלים")
        print("3. להוסיף פונקציונליות נוספת")
    else:
        print("\nיש בעיה ברישום הרופא")

if __name__ == "__main__":
    main()