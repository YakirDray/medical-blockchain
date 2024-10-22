from pathlib import Path
import json

def check_project_structure():
    print("בודק מבנה הפרויקט...\n")
    
    # הגדרת המבנה הרצוי
    required_structure = {
        'contracts/': {
            'MedicalRegistry.sol': 'קובץ החוזה'
        },
        'build/': {
            'MedicalRegistry.json': 'קובץ מקומפל',
            'contract_abi.json': 'קובץ ABI'
        },
        'src/': {
            'medical_system.py': 'קובץ המערכת',
            '__init__.py': 'קובץ אתחול'
        },
        '.env': 'קובץ הגדרות'
    }
    
    # בדיקת התיקיות והקבצים
    for path, content in required_structure.items():
        if isinstance(content, dict):
            # בדיקת תיקייה
            dir_path = Path(path)
            if not dir_path.exists():
                print(f"❌ חסרה תיקייה: {path}")
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"   ✓ נוצרה תיקייה: {path}")
            
            # בדיקת קבצים בתיקייה
            for file, description in content.items():
                file_path = dir_path / file
                if not file_path.exists():
                    print(f"❌ חסר קובץ: {file_path} ({description})")
                else:
                    print(f"✓ קיים: {file_path}")
        else:
            # בדיקת קובץ בודד
            file_path = Path(path)
            if not file_path.exists():
                print(f"❌ חסר קובץ: {path} ({content})")
            else:
                print(f"✓ קיים: {path}")
    
    return True

def create_abi():
    print("\nמנסה ליצור ABI...")
    try:
        # בדיקה אם קיים קובץ מקומפל
        compiled_path = Path('build/MedicalRegistry.json')
        if compiled_path.exists():
            with open(compiled_path, 'r') as f:
                compiled_data = json.load(f)
                
            # חילוץ ה-ABI
            abi = compiled_data['contracts']['MedicalRegistry.sol']['MedicalRegistry']['abi']
            
            # שמירת ה-ABI
            abi_path = Path('build/contract_abi.json')
            with open(abi_path, 'w') as f:
                json.dump(abi, f, indent=2)
                
            print(f"✓ נוצר קובץ ABI: {abi_path}")
            return True
    except Exception as e:
        print(f"❌ שגיאה ביצירת ABI: {str(e)}")
    return False

if __name__ == "__main__":
    check_project_structure()
    create_abi()