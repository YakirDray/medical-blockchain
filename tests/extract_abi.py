import json
from pathlib import Path

def extract_abi():
    print("מחלץ ABI מהחוזה המקומפל...")
    
    try:
        # יצירת תיקיית build אם לא קיימת
        build_dir = Path("build")
        build_dir.mkdir(exist_ok=True)
        
        # בדיקה אם קובץ החוזה המקומפל קיים
        contract_file = build_dir / "MedicalRegistry.json"
        if not contract_file.exists():
            raise FileNotFoundError("קובץ החוזה המקומפל לא נמצא. הרץ קודם compile_contract.py")
        
        # קריאת הקובץ המקומפל
        with open(contract_file, 'r') as f:
            compiled_contract = json.load(f)
        
        # חילוץ ה-ABI
        contract_abi = compiled_contract['contracts']['MedicalRegistry.sol']['MedicalRegistry']['abi']
        
        # שמירת ה-ABI בקובץ נפרד
        abi_file = build_dir / "contract_abi.json"
        with open(abi_file, 'w') as f:
            json.dump(contract_abi, f, indent=2)
        
        print(f"✅ ABI נשמר בהצלחה ב: {abi_file}")
        return True
        
    except Exception as e:
        print(f"❌ שגיאה בחילוץ ABI: {str(e)}")
        return False

if __name__ == "__main__":
    extract_abi()