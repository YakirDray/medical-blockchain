from pathlib import Path
import json
import shutil

def verify_files():
    print("בודק קבצים נדרשים...\n")
    
    # נתיבי הקבצים
    files = {
        'contract': Path('build/MedicalRegistry.json'),
        'abi': Path('build/contract_abi.json'),
        'env': Path('.env')
    }
    
    for name, path in files.items():
        if path.exists():
            print(f"✓ נמצא {name}: {path}")
            # בדיקת תוכן התיק עבור קבצי JSON
            if name in ['contract', 'abi']:
                try:
                    with open(path, 'r') as f:
                        json.load(f)
                    print(f"  ✓ קובץ JSON תקין")
                except json.JSONDecodeError:
                    print(f"  ❌ קובץ JSON לא תקין")
        else:
            print(f"❌ לא נמצא {name}: {path}")
    
    # בדיקת .env
    if files['env'].exists():
        with open(files['env'], 'r') as f:
            env_content = f.read()
            for var in ['PROVIDER_URL', 'ADMIN_PRIVATE_KEY', 'CONTRACT_ADDRESS']:
                if var not in env_content:
                    print(f"❌ חסר משתנה {var} בקובץ .env")

if __name__ == "__main__":
    verify_files()