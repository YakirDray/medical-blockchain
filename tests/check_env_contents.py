from dotenv import load_dotenv
import os

def check_env_contents():
    print("בודק תוכן קובץ .env...\n")
    
    load_dotenv()
    
    required_vars = {
        'PROVIDER_URL': 'כתובת הספק',
        'ADMIN_PRIVATE_KEY': 'מפתח פרטי',
        'CONTRACT_ADDRESS': 'כתובת החוזה'
    }
    
    all_present = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # הצגה מוסתרת של ערכים רגישים
            if var == 'ADMIN_PRIVATE_KEY':
                safe_value = value[:6] + '...' + value[-4:]
            else:
                safe_value = value
            print(f"✓ {var} = {safe_value}")
        else:
            print(f"❌ חסר {var} ({description})")
            all_present = False
    
    if all_present:
        print("\nכל המשתנים קיימים!")
    else:
        print("\nערכים נדרשים:")
        print("""
PROVIDER_URL=https://sepolia.infura.io/v3/32609b92970443b08f4e0a3e97d19dd5
ADMIN_PRIVATE_KEY=0xdbf4e83fac945a4772dc64cbde99d68b8af0652cbe6f7e3662b74d23129d6114
CONTRACT_ADDRESS=0x6A0336893177F45d8d23193D9a2564df471C5f0F
        """)
    
    return all_present

if __name__ == "__main__":
    check_env_contents()
    
    # הצגת נתיב מלא לקובץ
    import pathlib
    env_path = pathlib.Path('.env').absolute()
    print(f"\nנתיב מלא לקובץ .env:")
    print(env_path)