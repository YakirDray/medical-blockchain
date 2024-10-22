import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from medical_system import MedicalSystem
from medical_records import MedicalRecordSystem
from medical_analytics import MedicalAnalytics
from cryptography.fernet import Fernet
import base64

class MedicalGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("מערכת רפואית מבוזרת")
        self.root.geometry("800x600")
        
        # הגדרת RTL
        self.root.tk.call('encoding', 'system', 'utf-8')
        
        # אתחול מערכות
        self.medical_system = MedicalSystem()
        self.record_system = MedicalRecordSystem()
        self.analytics = MedicalAnalytics()
        
        # יצירת הממשק
        self.create_login_screen()  # מסך התחברות
        
        # יצירת מפתח הצפנה
        self.cipher_suite = Fernet(base64.urlsafe_b64encode(os.urandom(32)))

    def encrypt_password(self, password):
        """הצפנת הסיסמה"""
        encrypted_password = self.cipher_suite.encrypt(password.encode('utf-8'))
        return encrypted_password.decode('utf-8')

    def decrypt_password(self, encrypted_password):
        """פענוח הסיסמה"""
        decrypted_password = self.cipher_suite.decrypt(encrypted_password.encode('utf-8'))
        return decrypted_password.decode('utf-8')
    
    def create_login_screen(self):
        """מסך התחברות"""
        login_frame = ttk.Frame(self.root)
        login_frame.pack(pady=20)

        ttk.Label(login_frame, text="התחברות").pack(pady=10)

        ttk.Label(login_frame, text="שם משתמש:").pack(anchor="w", padx=10)
        self.username_entry = ttk.Entry(login_frame)
        self.username_entry.pack(padx=10, pady=5)

        ttk.Label(login_frame, text="סיסמה:").pack(anchor="w", padx=10)
        self.password_entry = ttk.Entry(login_frame, show="*")
        self.password_entry.pack(padx=10, pady=5)

        self.user_type = tk.StringVar()
        self.user_type.set("רופא")  # ברירת מחדל - רופא

        ttk.Radiobutton(login_frame, text="רופא", variable=self.user_type, value="רופא").pack(anchor="w", padx=10)
        ttk.Radiobutton(login_frame, text="מנהל", variable=self.user_type, value="מנהל").pack(anchor="w", padx=10)

        ttk.Button(login_frame, text="התחבר", command=self.login).pack(pady=10)

    def login(self):
        """בדיקת התחברות"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        user_type = self.user_type.get()

        if user_type == "מנהל":
            # התחברות מנהל
            if username == "admin" and password == "admin123":
                messagebox.showinfo("התחברות מוצלחת", "ברוך הבא, מנהל")
                self.clear_screen()
                self.create_admin_dashboard()
            else:
                messagebox.showerror("שגיאה", "שם משתמש או סיסמה שגויים למנהל")
        else:
            # התחברות רופא
            self.authenticate_doctor(username, password)

    def authenticate_doctor(self, license_number, password):
        """בדיקת אישור והתחברות רופא"""
        try:
            if os.path.exists('doctors.json'):
                with open('doctors.json', 'r') as f:
                    doctors = json.load(f)
                
                for address, doctor in doctors.items():
                    if doctor['email'] == license_number and self.decrypt_password(doctor['private_key']) == password:
                        if doctor['is_approved']:
                            messagebox.showinfo("התחברות מוצלחת", f"ברוך הבא, ד\"ר {doctor['name']}")
                            self.clear_screen()
                            self.create_doctor_dashboard(doctor['name'])
                        else:
                            messagebox.showerror("שגיאה", "הרופא עדיין לא אושר על ידי המנהל")
                        return
                
                messagebox.showerror("שגיאה", "רופא לא נמצא במערכת או סיסמה שגויה")
            else:
                messagebox.showerror("שגיאה", "לא נמצאו רופאים במערכת")
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה באימות רופא: {str(e)}")

    def clear_screen(self):
        """ניקוי המסך לצורך מעבר למסך הבא"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_admin_dashboard(self):
        """מסך מנהל - אישור רופאים"""
        admin_frame = ttk.Frame(self.root)
        admin_frame.pack(fill="both", expand=True)

        ttk.Label(admin_frame, text="ברוך הבא, מנהל", font=("Arial", 16)).pack(pady=10)

        # טבלת רופאים לאישור
        doctors_list_frame = ttk.LabelFrame(admin_frame, text="רופאים לאישור")
        doctors_list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.doctors_tree = ttk.Treeview(doctors_list_frame, columns=("name", "spec", "license", "status"), show="headings")
        self.doctors_tree.pack(fill="both", expand=True)

        self.doctors_tree.heading("name", text="שם")
        self.doctors_tree.heading("spec", text="התמחות")
        self.doctors_tree.heading("license", text="מספר רישיון")
        self.doctors_tree.heading("status", text="סטטוס")

        self.update_doctors_list()

        approve_button = ttk.Button(admin_frame, text="אישור רופא", command=self.approve_doctor)
        approve_button.pack(pady=10)

    def create_doctor_dashboard(self, doctor_name):
        """מסך רופא"""
        doctor_frame = ttk.Frame(self.root)
        doctor_frame.pack(fill="both", expand=True)

        ttk.Label(doctor_frame, text=f"ברוך הבא, ד\"ר {doctor_name}", font=("Arial", 16)).pack(pady=10)

        ttk.Label(doctor_frame, text="תוכן נוסף לרופאים יופיע כאן").pack(pady=20)

    def approve_doctor(self):
        """אישור רופא בטבלה"""
        selected_item = self.doctors_tree.selection()
        if not selected_item:
            messagebox.showerror("שגיאה", "יש לבחור רופא לאישור")
            return

        doctor_data = self.doctors_tree.item(selected_item)
        license_number = doctor_data['values'][2]

        try:
            with open('doctors.json', 'r') as f:
                doctors = json.load(f)
            
            for address, doctor in doctors.items():
                if doctor['license_number'] == license_number and not doctor.get('is_approved', False):
                    # אישור הרופא
                    doctor['is_approved'] = True
                    with open('doctors.json', 'w') as f:
                        json.dump(doctors, f, indent=2)
                    messagebox.showinfo("הצלחה", f"הרופא {doctor['name']} אושר בהצלחה!")
                    self.update_doctors_list()
                    return
            messagebox.showerror("שגיאה", "רופא זה כבר מאושר או לא נמצא במערכת")
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה באישור הרופא: {str(e)}")

    def update_doctors_list(self):
        """עדכון רשימת הרופאים בטבלה"""
        for item in self.doctors_tree.get_children():
            self.doctors_tree.delete(item)
        
        try:
            if os.path.exists('doctors.json'):
                with open('doctors.json', 'r') as f:
                    doctors = json.load(f)

                for address, doctor in doctors.items():
                    self.doctors_tree.insert('', 'end', values=(
                        doctor['name'],
                        doctor['specialization'],
                        doctor['license_number'],
                        'מאושר' if doctor['is_approved'] else 'ממתין לאישור'
                    ))
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בטעינת רשימת הרופאים: {str(e)}")

    def run(self):
        """הפעלת הממשק"""
        self.root.mainloop()

def main():
    gui = MedicalGUI()
    gui.run()

if __name__ == "__main__":
    main()
