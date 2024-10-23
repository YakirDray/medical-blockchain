import tkinter as tk
from tkinter import messagebox
import json
import os
from cryptography.fernet import Fernet
import base64
from web3 import Web3
from medical_system import MedicalSystem
from medical_records import MedicalRecordSystem
from medical_analytics import MedicalAnalytics

class MedicalGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("מערכת רפואית מבוזרת עם בלוקצ'יין")
        self.root.geometry("1024x768")

        # אתחול הצפנה
        self.cipher_suite = Fernet(base64.urlsafe_b64encode(os.urandom(32)))

        # אתחול מערכות רפואיות
        self.medical_system = MedicalSystem()
        self.record_system = MedicalRecordSystem()
        self.analytics = MedicalAnalytics()
        self.cipher_suite = Fernet(base64.urlsafe_b64encode(os.urandom(32)))
        self.init_encryption()

        # אתחול חיבור לבלוקצ'יין
        self.init_web3()

        # התחלת הממשק
        self.create_login_screen()

    def init_web3(self):
        """אתחול חיבור לבלוקצ'יין"""
        self.w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))  # שימוש ב-Ganache
        if not self.w3.is_connected():
            messagebox.showerror("שגיאה", "החיבור לבלוקצ'יין נכשל")
        else:
            messagebox.showinfo("הצלחה", "חיבור לבלוקצ'יין בוצע בהצלחה")

    def init_encryption(self):
        """אתחול מפתח הצפנה ושימוש במפתח קבוע"""
        key_file = 'encryption.key'
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                key = f.read()
        else:
            key = base64.urlsafe_b64encode(os.urandom(32))
            with open(key_file, 'wb') as f:
                f.write(key)

        self.cipher_suite = Fernet(key)

    def encrypt_password(self, password):
        """הצפנת הסיסמה"""
        encrypted_password = self.cipher_suite.encrypt(password.encode('utf-8'))
        return encrypted_password.decode('utf-8')

    def decrypt_password(self, encrypted_password):
        """פענוח הסיסמה"""
        decrypted_password = self.cipher_suite.decrypt(encrypted_password.encode('utf-8'))
        return decrypted_password.decode('utf-8')

    def clear_screen(self):
        """ניקוי המסך לצורך מעבר למסך חדש"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_login_screen(self):
        """מסך התחברות"""
        self.clear_screen()

        # מסגרת התחברות
        login_frame = tk.Frame(self.root)
        login_frame.pack(pady=20)

        # שם משתמש
        tk.Label(login_frame, text="התחברות למערכת רפואית").pack(pady=10)
        tk.Label(login_frame, text="שם משתמש:").pack(anchor="w", padx=10)
        self.username_entry = tk.Entry(login_frame, width=40)
        self.username_entry.pack(padx=10, pady=5)

        # סיסמה
        tk.Label(login_frame, text="סיסמה:").pack(anchor="w", padx=10)
        self.password_entry = tk.Entry(login_frame, show="*", width=40)
        self.password_entry.pack(padx=10, pady=5)

        # סוג משתמש
        self.user_type = tk.StringVar()
        self.user_type.set("רופא")

        tk.Radiobutton(login_frame, text="רופא", variable=self.user_type, value="רופא").pack(anchor="w", padx=10)
        tk.Radiobutton(login_frame, text="מנהל", variable=self.user_type, value="מנהל").pack(anchor="w", padx=10)

        # כפתור התחברות
        tk.Button(login_frame, text="התחבר", command=self.login).pack(pady=10)

        # כפתור הרשמה
        tk.Button(login_frame, text="הירשם כרופא חדש", command=self.create_registration_screen).pack(pady=10)

    def send_transaction(self, to_address, value_in_ether):
        try:
            # כתובת השולח - חשבון מנהל
            sender_address = self.w3.eth.accounts[0]  # חשבון 0 מ-Ganache

            # הכנת טרנזקציה
            transaction = {
                'to': to_address,
                'from': sender_address,
                'value': self.w3.toWei(value_in_ether, 'ether'),
                'gas': 21000,
                'gasPrice': self.w3.toWei('50', 'gwei')
            }

            # שליחת הטרנזקציה
            tx_hash = self.w3.eth.send_transaction(transaction)
            messagebox.showinfo("הצלחה", f"טרנזקציה נשלחה בהצלחה! Hash: {tx_hash.hex()}")
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בשליחת הטרנזקציה: {str(e)}")

    def create_registration_screen(self):
        """מסך הרשמה לרופא"""
        self.clear_screen()

        # מסגרת הרשמה
        reg_frame = tk.Frame(self.root)
        reg_frame.pack(pady=20)

        tk.Label(reg_frame, text="הרשמה לרופא חדש").pack(pady=10)

        fields = [
            ("שם מלא:", "name"),
            ("מספר רישיון:", "license"),
            ("התמחות:", "specialization"),
            ("אימייל:", "email"),
            ("סיסמה:", "password"),
            ("אימות סיסמה:", "password_confirm")
        ]

        self.reg_entries = {}
        for label_text, field_name in fields:
            tk.Label(reg_frame, text=label_text).pack(anchor="w", padx=10)
            entry = tk.Entry(reg_frame, show="*" if "password" in field_name else "", width=40)
            entry.pack(padx=10, pady=5)
            self.reg_entries[field_name] = entry

        # כפתור הרשמה
        tk.Button(reg_frame, text="הרשם", command=self.register_doctor).pack(pady=10)
        tk.Button(reg_frame, text="חזור", command=self.create_login_screen).pack(pady=5)

    def register_doctor(self):
        """רישום רופא חדש"""
        data = {field: entry.get().strip() for field, entry in self.reg_entries.items()}

        # בדיקת שדות חובה
        if not all(data.values()):
            messagebox.showerror("שגיאה", "נא למלא את כל השדות")
            return
        
        # בדיקת התאמת סיסמאות
        if data["password"] != data["password_confirm"]:
            messagebox.showerror("שגיאה", "הסיסמאות אינן תואמות")
            return
        encrypted_password = self.encrypt_password(data["password"])
        print(f"Password: {data['password']}, Encrypted: {encrypted_password}")
        
        # שמירת נתוני הרופא
        doctor_data = {
            "name": data["name"],
            "license_number": data["license"],
            "specialization": data["specialization"],
            "email": data["email"],
            "private_key": self.encrypt_password(data["password"]),
            "is_approved": False  # דרוש אישור מנהל
        }

        if os.path.exists('doctors.json'):
            with open('doctors.json', 'r') as f:
                doctors = json.load(f)
        else:
            doctors = {}

        # שמירת הרופא החדש בקובץ
        doctors[data["license"]] = doctor_data
        with open('doctors.json', 'w') as f:
            json.dump(doctors, f, indent=2)

        messagebox.showinfo("הצלחה", "הרשמה בוצעה בהצלחה! המתן לאישור מנהל.")
        self.create_login_screen()

    def login(self):
        """טיפול בהתחברות"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        user_type = self.user_type.get()

        if user_type == "מנהל":
            if self.verify_admin(username, password):
                messagebox.showinfo("התחברות מוצלחת", "ברוך הבא, מנהל")
                self.clear_screen()
                self.create_admin_dashboard()
            else:
                messagebox.showerror("שגיאה", "שם משתמש או סיסמה שגויים למנהל")
        else:
            self.authenticate_doctor(username, password)

    def verify_admin(self, username, password):
        """אימות פרטי מנהל"""
        if username == "admin" and password == "admin123":  # ערך ברירת מחדל
            return True
        return False

    def authenticate_doctor(self, email, password):
        try:
            if os.path.exists('doctors.json'):
                with open('doctors.json', 'r') as f:
                    doctors = json.load(f)
                
                for doctor in doctors.values():
                    if doctor['email'] == email:
                        # פענוח הסיסמה המוצפנת והשוואה עם הסיסמה המוזנת
                        stored_password = self.decrypt_password(doctor['private_key'])
                        print(f"Entered: {password}, Decrypted Stored: {stored_password}")
                        if password == stored_password:
                            if doctor['is_approved']:
                                messagebox.showinfo("התחברות מוצלחת", f"ברוך הבא, ד\"ר {doctor['name']}")
                                self.clear_screen()
                                self.create_doctor_dashboard(doctor['name'])
                            else:
                                messagebox.showerror("שגיאה", "הרופא עדיין לא אושר על ידי המנהל")
                            return
                        else:
                            messagebox.showerror("שגיאה", "סיסמה שגויה")
                            return
                messagebox.showerror("שגיאה", "רופא לא נמצא במערכת")
            else:
                messagebox.showerror("שגיאה", "לא נמצאו רופאים במערכת")
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה באימות רופא: {str(e)}")

    def create_admin_dashboard(self):
        """מסך מנהל - אישור רופאים והצגת סטטיסטיקות"""
        self.clear_screen()
        admin_frame = tk.Frame(self.root)
        admin_frame.pack(fill="both", expand=True)

        tk.Label(admin_frame, text="ברוך הבא, מנהל", font=("Arial", 16)).pack(pady=10)

        # הצגת סטטיסטיקות
        stats_frame = tk.LabelFrame(admin_frame, text="סטטיסטיקות מערכת")
        stats_frame.pack(fill="x", padx=10, pady=10)

        stats = self.get_system_stats()
        stats_labels = [
            f"סה\"כ רופאים: {stats['total_doctors']}",
            f"רופאים מאושרים: {stats['approved_doctors']}",
            f"רופאים ממתינים לאישור: {stats['pending_doctors']}",
        ]

        for stat in stats_labels:
            tk.Label(stats_frame, text=stat).pack(anchor="w", padx=10, pady=5)

        # אישור רופאים
        doctors_list_frame = tk.Frame(admin_frame)
        doctors_list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.doctors_tree = tk.Listbox(doctors_list_frame)
        self.doctors_tree.pack(fill="both", expand=True)

        self.update_doctors_list()

        tk.Button(admin_frame, text="אישור רופא", command=self.approve_doctor).pack(pady=10)

    def get_system_stats(self):
        """חישוב סטטיסטיקות המערכת"""
        stats = {
            "total_doctors": 0,
            "approved_doctors": 0,
            "pending_doctors": 0,
        }

        try:
            if os.path.exists('doctors.json'):
                with open('doctors.json', 'r') as f:
                    doctors = json.load(f)
                stats["total_doctors"] = len(doctors)
                stats["approved_doctors"] = sum(1 for doctor in doctors.values() if doctor["is_approved"])
                stats["pending_doctors"] = stats["total_doctors"] - stats["approved_doctors"]
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בחישוב הסטטיסטיקות: {str(e)}")

        return stats

    def update_doctors_list(self):
        """עדכון רשימת הרופאים בטבלה"""
        self.doctors_tree.delete(0, tk.END)

        try:
            if os.path.exists('doctors.json'):
                with open('doctors.json', 'r') as f:
                    doctors = json.load(f)

                for doctor in doctors.values():
                    self.doctors_tree.insert(tk.END, f"{doctor['name']} - {doctor['license_number']} - {'מאושר' if doctor['is_approved'] else 'ממתין לאישור'}")
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בטעינת רשימת הרופאים: {str(e)}")

    def approve_doctor(self):
        selected_item = self.doctors_tree.curselection()
        if not selected_item:
            messagebox.showerror("שגיאה", "יש לבחור רופא לאישור")
            return

        doctor_data = self.doctors_tree.get(selected_item)
        license_number = doctor_data.split(" - ")[1]  # חיתוך מספר רישיון מהרשימה

        try:
            with open('doctors.json', 'r') as f:
                doctors = json.load(f)

            if license_number in doctors:
                doctors[license_number]["is_approved"] = True

                # שמירת האישור בקובץ
                with open('doctors.json', 'w') as f:
                    json.dump(doctors, f, indent=2)

                # ביצוע טרנזקציה להוספת הרופא בבלוקצ'יין
                doctor_address = doctors[license_number]["email"]  # נניח שהכתובת היא האימייל
                self.send_transaction(doctor_address, 0.000000001)  # טרנזקציה של 0.01 ETH

                messagebox.showinfo("הצלחה", "הרופא אושר בהצלחה!")
                self.update_doctors_list()
            else:
                messagebox.showerror("שגיאה", "הרופא לא נמצא במערכת")
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה באישור הרופא: {str(e)}")

    def create_patient_transaction(self, patient_address, value_in_ether):
        try:
            # כתובת הרופא
            doctor_address = self.w3.eth.accounts[0]  # חשבון הרופא
            
            # הכנת טרנזקציה
            transaction = {
                'to': patient_address,
                'from': doctor_address,
                'value': self.w3.toWei(value_in_ether, 'ether'),
                'gas': 21000,
                'gasPrice': self.w3.toWei('50', 'gwei')
            }

            # שליחת הטרנזקציה
            tx_hash = self.w3.eth.send_transaction(transaction)
            messagebox.showinfo("הצלחה", f"טרנזקציה נשלחה בהצלחה! Hash: {tx_hash.hex()}")
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בשליחת הטרנזקציה: {str(e)}")
    
    def create_doctor_dashboard(self, doctor_name):
        doctor_frame = tk.Frame(self.root)
        doctor_frame.pack(fill="both", expand=True)

        tk.Label(doctor_frame, text=f"ברוך הבא, ד\"ר {doctor_name}", font=("Arial", 16)).pack(pady=10)

        tk.Label(doctor_frame, text="כתובת מטופל:").pack(anchor="w", padx=10)
        self.patient_address_entry = tk.Entry(doctor_frame, width=40)
        self.patient_address_entry.pack(padx=10, pady=5)

        tk.Label(doctor_frame, text="כמות ETH לשליחה:").pack(anchor="w", padx=10)
        self.amount_entry = tk.Entry(doctor_frame, width=40)
        self.amount_entry.pack(padx=10, pady=5)

        tk.Button(doctor_frame, text="שלח טרנזקציה", command=self.send_patient_transaction).pack(pady=10)

    def send_patient_transaction(self):
        patient_address = self.patient_address_entry.get()
        amount = float(self.amount_entry.get())
        self.create_patient_transaction(patient_address, amount)

    def run(self):
        """הפעלת הממשק"""
        self.root.mainloop()

def main():
    gui = MedicalGUI()
    gui.run()

if __name__ == "__main__":
    main()
