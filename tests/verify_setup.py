from pathlib import Path
import json
import shutil

def verify_setup():
    print("בודק הגדרות מערכת...\n")
    
    # בדיקת מבנה תיקיות
    current_dir = Path.cwd()
    print(f"תיקייה נוכחית: {current_dir}")
    
    # רשימת קבצים נדרשים
    required_files = {
        'build/contract_abi.json': 'קובץ ABI',
        'build/MedicalRegistry.json': 'קובץ חוזה מקומפל',
        '.env': 'קובץ הגדרות',
        'src/medical_system.py': 'קובץ המערכת'
    }
    
    all_good = True
    
    for file_path, description in required_files.items():
        full_path = current_dir / file_path
        if full_path.exists():
            print(f"✓ נמצא {description}: {full_path}")
            
            # בדיקת קבצי JSON
            if file_path.endswith('.json'):
                try:
                    with open(full_path, 'r') as f:
                        json.load(f)
                    print(f"  ✓ תוכן JSON תקין")
                except json.JSONDecodeError:
                    print(f"  ❌ תוכן JSON לא תקין")
                    all_good = False
        else:
            print(f"❌ חסר {description}: {full_path}")
            all_good = False
    
    # הצגת תוכן תיקיית build
    build_dir = current_dir / 'build'
    if build_dir.exists():
        print("\nקבצים בתיקיית build:")
        for file in build_dir.iterdir():
            print(f"- {file.name}")
    
    return all_good

if __name__ == "__main__":
    verify_setup()