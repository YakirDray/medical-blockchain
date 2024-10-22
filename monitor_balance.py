from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
import os
import time
from datetime import datetime

def monitor_balance_with_alerts():
    try:
        # טעינת הגדרות
        load_dotenv()
        w3 = Web3(Web3.HTTPProvider(os.getenv('PROVIDER_URL')))
        account = Account.from_key(os.getenv('ADMIN_PRIVATE_KEY'))
        
        print(f"מנטר כתובת: {account.address}")
        print("מחכה לקבלת ETH...")
        print("הניטור יתריע אוטומטית כשיגיע ETH")
        print("לחץ Ctrl+C לעצירה\n")
        
        start_time = time.time()
        previous_balance = w3.eth.get_balance(account.address)
        check_count = 0
        
        while True:
            try:
                current_balance = w3.eth.get_balance(account.address)
                current_balance_eth = w3.from_wei(current_balance, 'ether')
                
                # בדיקת שינוי ביתרה
                if current_balance > previous_balance:
                    amount_received = w3.from_wei(current_balance - previous_balance, 'ether')
                    print(f"\n🎉 התקבל ETH!")
                    print(f"סכום שהתקבל: {amount_received} ETH")
                    print(f"יתרה נוכחית: {current_balance_eth} ETH")
                    
                    if current_balance_eth >= 0.1:
                        print("\n✅ יש מספיק ETH להתקנת החוזה!")
                        return True
                
                # הצגת סטטוס
                elapsed = int(time.time() - start_time)
                minutes, seconds = divmod(elapsed, 60)
                check_count += 1
                
                status = f"\rזמן המתנה: {minutes:02d}:{seconds:02d} | "
                status += f"בדיקות: {check_count} | "
                status += f"יתרה: {current_balance_eth:.6f} ETH"
                print(status, end='')
                
                previous_balance = current_balance
                time.sleep(5)
                
            except Exception as e:
                print(f"\nשגיאה בבדיקת היתרה: {str(e)}")
                time.sleep(10)
                continue
                
    except KeyboardInterrupt:
        print("\n\nניטור הופסק ידנית")
        return False
    except Exception as e:
        print(f"\nשגיאה: {str(e)}")
        return False

if __name__ == "__main__":
    monitor_balance_with_alerts()