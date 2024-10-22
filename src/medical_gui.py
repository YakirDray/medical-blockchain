import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from medical_system import MedicalSystem
from medical_records import MedicalRecordSystem
from medical_analytics import MedicalAnalytics

class MedicalGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("מערכת רפואית מבוזרת")
        self.root.geometry("1000x600")
        
        # הגדרת RTL
        self.root.tk.call('encoding', 'system', 'utf-8')
        
        # אתחול מערכות
        self.medical_system = MedicalSystem()
        self.record_system = MedicalRecordSystem()
        self.analytics = MedicalAnalytics()
        
        # יצירת הממשק
        self.create_gui()
    
    def register_doctor(self):
        """רישום רופא חדש"""
        try:
            name = self.doctor_name.get()
            specialization = self.doctor_spec.get()
            license_number = self.doctor_license.get()
            email = self.doctor_email.get()
            
            # בדיקת תקינות שדות
            if not all([name, specialization, license_number, email]):
                messagebox.showerror("שגיאה", "יש למלא את כל השדות")
                return
            
            # רישום הרופא
            result = self.medical_system.register_doctor(
                name=name,
                specialization=specialization,
                license_number=license_number,
                email=email
            )
            
            if result:
                messagebox.showinfo("הצלחה", "הרופא נרשם בהצלחה!")
                self.update_doctors_list()
                
                # ניקוי שדות
                self.doctor_name.delete(0, tk.END)
                self.doctor_spec.delete(0, tk.END)
                self.doctor_license.delete(0, tk.END)
                self.doctor_email.delete(0, tk.END)
            
        except Exception as e:
            messagebox.showerror("שגיאה", str(e))
    
    def update_doctors_list(self):
        """עדכון רשימת הרופאים בטבלה"""
        # ניקוי הטבלה הקיימת
        for item in self.doctors_tree.get_children():
            self.doctors_tree.delete(item)
        
        try:
            # טעינת רשימת הרופאים
            if os.path.exists('doctors.json'):
                with open('doctors.json', 'r') as f:
                    doctors = json.load(f)
                    
                for address, doctor in doctors.items():
                    self.doctors_tree.insert('', 'end', values=(
                        doctor['name'],
                        doctor['specialization'],
                        doctor['license_number'],
                        'מאושר' if doctor.get('is_approved', False) else 'ממתין לאישור'
                    ))
                    
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בטעינת רשימת הרופאים: {str(e)}")
    
    def create_doctors_tab(self):
        """טאב ניהול רופאים"""
        doctors_frame = ttk.Frame(self.notebook)
        self.notebook.add(doctors_frame, text="ניהול רופאים")
        
        # טופס רישום רופא
        reg_frame = ttk.LabelFrame(doctors_frame, text="רישום רופא חדש")
        reg_frame.pack(fill="x", padx=10, pady=5)
        
        # שדות הטופס
        fields = [
            ("שם:", "doctor_name"),
            ("התמחות:", "doctor_spec"),
            ("מספר רישיון:", "doctor_license"),
            ("אימייל:", "doctor_email")
        ]
        
        for i, (label, attr) in enumerate(fields):
            ttk.Label(reg_frame, text=label).grid(row=i, column=0, padx=5, pady=5)
            entry = ttk.Entry(reg_frame)
            entry.grid(row=i, column=1, padx=5, pady=5)
            setattr(self, attr, entry)
        
        ttk.Button(reg_frame, text="רישום רופא",
                  command=self.register_doctor).grid(row=len(fields), column=0, columnspan=2, pady=10)
        
        # רשימת רופאים
        list_frame = ttk.LabelFrame(doctors_frame, text="רשימת רופאים")
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("name", "spec", "license", "status")
        self.doctors_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # הגדרת כותרות
        headers = {
            "name": "שם",
            "spec": "התמחות",
            "license": "מספר רישיון",
            "status": "סטטוס"
        }
        
        for col, header in headers.items():
            self.doctors_tree.heading(col, text=header)
            self.doctors_tree.column(col, width=100)
        
        self.doctors_tree.pack(fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.doctors_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.doctors_tree.configure(yscrollcommand=scrollbar.set)
    
    def create_gui(self):
        """יצירת הממשק הגרפי"""
        # תפריט ראשי
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # תפריט קובץ
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="קובץ", menu=file_menu)
        file_menu.add_command(label="יציאה", command=self.root.quit)
        
        # Notebook לניהול טאבים
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)
        
        # טאבים
        self.create_doctors_tab()
        # בהמשך נוסיף טאבים נוספים
    
    def run(self):
        """הפעלת הממשק"""
        # עדכון ראשוני של הרשימות
        self.update_doctors_list()
        
        # הפעלת החלון
        self.root.mainloop()

def main():
    gui = MedicalGUI()
    gui.run()

if __name__ == "__main__":
    main()