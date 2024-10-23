import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from ttkthemes import ThemedTk
from cryptography.fernet import Fernet
import base64
from typing import Dict, Any, Optional
from medical_system import MedicalSystem
from medical_records import MedicalRecordSystem

class MedicalGUI:
    def __init__(self):
        # אתחול חלון ראשי
        self.root = ThemedTk(theme="arc")
        self.root.title("מערכת רפואית")
        self.root.geometry("1024x768")
        
        # הגדרות RTL ועיצוב
        self.root.tk.call('encoding', 'system', 'utf-8')
        
        # אתחול מערכות
        self.init_systems()
        self.setup_styles()
        self.init_encryption()
        
        # משתני מצב
        self.current_user = None
        self.current_user_type = None
        
        # התחלת המערכת
        self.create_login_screen()

    def init_systems(self):
        """אתחול המערכות"""
        try:
            self.medical_system = MedicalSystem()
            self.record_system = MedicalRecordSystem()
        except Exception as e:
            messagebox.showerror("שגיאת אתחול", f"שגיאה באתחול המערכת: {str(e)}")
            self.root.destroy()

    def init_encryption(self):
        """אתחול מערכת ההצפנה"""
        try:
            key_file = 'encryption.key'
            if os.path.exists(key_file):
                with open(key_file, 'rb') as f:
                    key = f.read()
            else:
                key = base64.urlsafe_b64encode(os.urandom(32))
                with open(key_file, 'wb') as f:
                    f.write(key)
            self.cipher_suite = Fernet(key)
        except Exception as e:
            messagebox.showerror("שגיאת הצפנה", f"שגיאה באתחול מערכת ההצפנה: {str(e)}")
            self.root.destroy()

    def setup_styles(self):
        """הגדרת סגנונות עיצוב"""
        style = ttk.Style()
        
        # כפתורים
        style.configure(
            "Action.TButton",
            padding=10,
            font=("Segoe UI", 10),
            background="#007bff",
            foreground="white"
        )
        
        # כפתורי משנה
        style.configure(
            "Secondary.TButton",
            padding=8,
            font=("Segoe UI", 9),
            background="#6c757d"
        )
        
        # תוויות
        style.configure(
            "Main.TLabel",
            font=("Segoe UI", 11),
            padding=5
        )
        
        # כותרות
        style.configure(
            "Title.TLabel",
            font=("Segoe UI", 16, "bold"),
            padding=15
        )
        
        # שדות קלט
        style.configure(
            "Main.TEntry",
            padding=8,
            font=("Segoe UI", 10)
        )
        
        # מסגרות
        style.configure(
            "Card.TFrame",
            padding=20,
            relief="raised"
        )

    def encrypt_password(self, password: str) -> str:
        """הצפנת סיסמה"""
        return self.cipher_suite.encrypt(password.encode()).decode()

    def decrypt_password(self, encrypted_password: str) -> str:
        """פענוח סיסמה"""
        return self.cipher_suite.decrypt(encrypted_password.encode()).decode()

    def clear_screen(self):
        """ניקוי המסך"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_login_screen(self):
        """יצירת מסך התחברות"""
        self.clear_screen()
        
        # מסגרת התחברות
        login_frame = ttk.Frame(self.root, style="Card.TFrame")
        login_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # כותרת
        ttk.Label(
            login_frame,
            text="התחברות למערכת",
            style="Title.TLabel"
        ).pack(pady=(0, 20))
        
        # שדות התחברות
        credentials_frame = ttk.Frame(login_frame)
        credentials_frame.pack(fill="x", padx=30, pady=10)
        
        # שם משתמש
        ttk.Label(
            credentials_frame,
            text="שם משתמש/אימייל:",
            style="Main.TLabel"
        ).pack(anchor="w")
        
        self.username_entry = ttk.Entry(
            credentials_frame,
            width=30,
            style="Main.TEntry"
        )
        self.username_entry.pack(fill="x", pady=(2, 10))
        
        # סיסמה
        ttk.Label(
            credentials_frame,
            text="סיסמה:",
            style="Main.TLabel"
        ).pack(anchor="w")
        
        self.password_entry = ttk.Entry(
            credentials_frame,
            width=30,
            show="●",
            style="Main.TEntry"
        )
        self.password_entry.pack(fill="x", pady=(2, 10))
        
        # בחירת סוג משתמש
        user_type_frame = ttk.Frame(credentials_frame)
        user_type_frame.pack(fill="x", pady=10)
        
        self.user_type = tk.StringVar(value="doctor")
        
        ttk.Radiobutton(
            user_type_frame,
            text="רופא",
            variable=self.user_type,
            value="doctor"
        ).pack(side="right", padx=10)
        
        ttk.Radiobutton(
            user_type_frame,
            text="מנהל",
            variable=self.user_type,
            value="admin"
        ).pack(side="right")
        
        # כפתורים
        buttons_frame = ttk.Frame(login_frame)
        buttons_frame.pack(fill="x", pady=20)
        
        ttk.Button(
            buttons_frame,
            text="התחבר",
            command=self.login,
            style="Action.TButton",
            width=20
        ).pack(side="right", padx=5)
        
        ttk.Button(
            buttons_frame,
            text="הרשמה",
            command=self.show_registration,
            style="Secondary.TButton",
            width=20
        ).pack(side="right", padx=5)
        
        # סטטוס
        self.status_label = ttk.Label(
            login_frame,
            text="",
            style="Main.TLabel"
        )
        self.status_label.pack(pady=(0, 10))

    def login(self):
        """טיפול בהתחברות"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        user_type = self.user_type.get()
        
        if not username or not password:
            messagebox.showerror("שגיאה", "נא למלא את כל השדות")
            return
        
        try:
            if user_type == "admin":
                if self.verify_admin(username, password):
                    self.current_user = {"type": "admin", "username": username}
                    self.create_admin_dashboard()
                else:
                    messagebox.showerror("שגיאה", "פרטי התחברות שגויים")
            else:
                doctor = self.verify_doctor(username, password)
                if doctor:
                    self.current_user = {"type": "doctor", "data": doctor}
                    self.create_doctor_dashboard(doctor["name"])
                else:
                    messagebox.showerror("שגיאה", "פרטי התחברות שגויים")
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בהתחברות: {str(e)}")

    def verify_admin(self, username: str, password: str) -> bool:
        """אימות פרטי מנהל"""
        try:
            admin_file = 'admin_credentials.json'
            if not os.path.exists(admin_file):
                # יצירת קובץ ברירת מחדל
                default_admin = {
                    "admin": {
                        "password": self.encrypt_password("admin123"),
                        "role": "admin",
                        "name": "מנהל מערכת",
                        "email": "admin@medical.com"
                    }
                }
                with open(admin_file, 'w', encoding='utf-8') as f:
                    json.dump(default_admin, f, ensure_ascii=False, indent=4)
            
            with open(admin_file, 'r', encoding='utf-8') as f:
                admins = json.load(f)
            
            if username == "admin" and password == "admin123":
                return True
            elif username in admins:
                stored_pass = self.decrypt_password(admins[username]["password"])
                return password == stored_pass
                
            return False
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה באימות מנהל: {str(e)}")
            return False

    def verify_doctor(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """אימות פרטי רופא"""
        try:
            doctors = self.medical_system.get_doctors()
            for doctor in doctors.values():
                if doctor["email"] == email:
                    stored_password = self.decrypt_password(doctor["private_key"])
                    if password == stored_password:
                        if doctor["is_approved"]:
                            return doctor
                        else:
                            messagebox.showwarning("אזהרה", "חשבונך עדיין לא אושר על ידי מנהל")
                            return None
            return None
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה באימות: {str(e)}")
            return None

    def show_registration(self):
        """מעבר למסך הרשמה"""
        self.create_registration_screen()

    def logout(self):
        """התנתקות מהמערכת"""
        self.current_user = None
        self.create_login_screen()

    def run(self):
        """הפעלת המערכת"""
        self.root.mainloop()
    def create_registration_screen(self):
        self.clear_screen()
        
        reg_frame = ttk.Frame(self.root, style="Card.TFrame")
        reg_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ttk.Label(
            reg_frame,
            text="הרשמת רופא חדש",
            style="Title.TLabel"
        ).pack(pady=(0, 20))
        
        # טופס הרשמה
        form_frame = ttk.Frame(reg_frame)
        form_frame.pack(fill="x", padx=30, pady=10)
        
        fields = [
            ("שם מלא:", "name"),
            ("מספר רישיון:", "license"),
            ("התמחות:", "specialization"),
            ("אימייל:", "email"),
            ("סיסמה:", "password", True),
            ("אימות סיסמה:", "password_confirm", True)
        ]
        
        self.reg_entries = {}
        for label_text, field_name, *args in fields:
            field_frame = ttk.Frame(form_frame)
            field_frame.pack(fill="x", pady=5)
            
            ttk.Label(
                field_frame,
                text=label_text,
                style="Main.TLabel"
            ).pack(anchor="w")
            
            show = "●" if args and args[0] else ""
            entry = ttk.Entry(
                field_frame,
                style="Main.TEntry",
                show=show
            )
            entry.pack(fill="x", pady=(2, 5))
            self.reg_entries[field_name] = entry
        
        # כפתורי פעולה
        buttons_frame = ttk.Frame(reg_frame)
        buttons_frame.pack(fill="x", pady=20)
        
        ttk.Button(
            buttons_frame,
            text="הרשם",
            command=self.register_doctor,
            style="Action.TButton",
            width=20
        ).pack(side="right", padx=5)
        
        ttk.Button(
            buttons_frame,
            text="חזור",
            command=self.create_login_screen,
            style="Secondary.TButton",
            width=20
        ).pack(side="right", padx=5)

    def register_doctor(self):
        """רישום רופא חדש"""
        try:
            # איסוף נתונים מהטופס
            data = {field: entry.get().strip() for field, entry in self.reg_entries.items()}
            
            # בדיקות תקינות
            if not all(data.values()):
                messagebox.showerror("שגיאה", "נא למלא את כל השדות")
                return
                
            if data["password"] != data["password_confirm"]:
                messagebox.showerror("שגיאה", "הסיסמאות אינן תואמות")
                return
                
            # הכנת נתוני הרופא
            doctor_data = {
                "name": data["name"],
                "specialization": data["specialization"],
                "license": data["license"],
                "email": data["email"],
                "private_key": self.encrypt_password(data["password"])
            }
            
            # רישום במערכת
            success = self.medical_system.register_doctor(doctor_data)
            
            if success:
                messagebox.showinfo(
                    "הרשמה מוצלחת",
                    "ההרשמה בוצעה בהצלחה. המתן לאישור מנהל המערכת."
                )
                self.create_login_screen()
            else:
                messagebox.showerror("שגיאה", "שגיאה ברישום הרופא")
                
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה ברישום: {str(e)}")

    def create_admin_dashboard(self):
        """יצירת לוח בקרה למנהל"""
        self.clear_screen()
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # כותרת וסרגל עליון
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(
            header_frame,
            text="ניהול המערכת",
            style="Title.TLabel"
        ).pack(side="right")
        
        ttk.Button(
            header_frame,
            text="התנתק",
            command=self.logout,
            style="Secondary.TButton"
        ).pack(side="left")
        
        # סטטיסטיקה
        stats_frame = ttk.LabelFrame(main_frame, text="סטטיסטיקה כללית")
        stats_frame.pack(fill="x", pady=(0, 20))
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(padx=10, pady=10)
        
        stats = self.medical_system.get_system_stats()
        
        stats_data = [
            ("סה\"כ רופאים", stats["total_doctors"]),
            ("ממתינים לאישור", stats["pending_doctors"]),
            ("רופאים פעילים", stats["active_doctors"]),
            ("מטופלים פעילים", stats["active_patients"])
        ]
        
        for col, (title, value) in enumerate(stats_data):
            self.create_stat_widget(stats_grid, title, str(value), 0, col)
        
        # ניהול רופאים
        doctors_frame = ttk.LabelFrame(main_frame, text="ניהול רופאים")
        doctors_frame.pack(fill="both", expand=True)
        
        # סרגל כלים
        toolbar = ttk.Frame(doctors_frame)
        toolbar.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(
            toolbar,
            text="אשר נבחרים",
            command=self.approve_selected_doctors,
            style="Action.TButton"
        ).pack(side="right", padx=5)
        
        ttk.Button(
            toolbar,
            text="רענן רשימה",
            command=self.update_doctors_list,
            style="Secondary.TButton"
        ).pack(side="right", padx=5)
        
        # טבלת רופאים
        self.create_doctors_table(doctors_frame)

    def create_doctor_dashboard(self, doctor_name):
        """יצירת לוח בקרה לרופא"""
        self.clear_screen()
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # כותרת וסרגל עליון
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(
            header_frame,
            text=f"שלום, ד\"ר {doctor_name}",
            style="Title.TLabel"
        ).pack(side="right")
        
        ttk.Button(
            header_frame,
            text="התנתק",
            command=self.logout,
            style="Secondary.TButton"
        ).pack(side="left")
        
        # לשוניות
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True)
        
        # לשונית מטופלים
        self.create_patients_tab(notebook)
        
        # לשונית רשומות רפואיות
        self.create_records_tab(notebook)

    def create_patients_tab(self, parent):
        """יצירת לשונית מטופלים"""
        frame = ttk.Frame(parent)
        
        # סרגל כלים
        toolbar = ttk.Frame(frame)
        toolbar.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(
            toolbar,
            text="הוסף מטופל",
            command=self.add_patient,
            style="Action.TButton"
        ).pack(side="right", padx=5)
        
        ttk.Button(
            toolbar,
            text="צפה בפרטים",
            command=self.view_patient,
            style="Secondary.TButton"
        ).pack(side="right", padx=5)
        
        # טבלת מטופלים
        columns = ("id", "name", "age", "last_visit", "status")
        
        self.patients_tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings"
        )
        
        headers = {
            "id": "ת.ז.",
            "name": "שם מלא",
            "age": "גיל",
            "last_visit": "ביקור אחרון",
            "status": "סטטוס"
        }
        
        for col in columns:
            self.patients_tree.heading(col, text=headers[col])
            self.patients_tree.column(col, width=100)
        
        self.patients_tree.pack(fill="both", expand=True)
        
        # עדכון הרשימה
        self.update_patients_list()
        
        parent.add(frame, text="המטופלים שלי")

    def create_records_tab(self, parent):
        """יצירת לשונית רשומות רפואיות"""
        frame = ttk.Frame(parent)
        parent.add(frame, text="רשומות רפואיות")
        
        # סרגל כלים
        toolbar = ttk.Frame(frame)
        toolbar.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(
            toolbar,
            text="צור רשומה",
            command=self.add_medical_record,
            style="Action.TButton"
        ).pack(side="right", padx=5)
        
        ttk.Button(
            toolbar,
            text="צפה ברשומה",
            command=self.view_medical_record,
            style="Secondary.TButton"
        ).pack(side="right", padx=5)
        
        # טבלת רשומות
        columns = ("patient", "date", "type", "description")
        
        self.records_tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings"
        )
        
        headers = {
            "patient": "מטופל",
            "date": "תאריך",
            "type": "סוג רשומה",
            "description": "תיאור"
        }
        
        for col in columns:
            self.records_tree.heading(col, text=headers[col])
            self.records_tree.column(col, width=100)
        
        self.records_tree.pack(fill="both", expand=True)
        
        # עדכון הרשימה
        self.update_records_list()


    def view_medical_record(self):
     selection = self.records_tree.selection()
     if not selection:
        messagebox.showwarning("אזהרה", "נא לבחור רשומה")
        return

     record_id = self.records_tree.item(selection[0])["values"][0]

     try:
        record = self.record_system.get_medical_record(record_id)
        
        if not record:
            messagebox.showerror("שגיאה", "רשומה לא נמצאה")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title(f"פרטי רשומה - {record['type']}")
        dialog.geometry("600x400")

        # Display medical record details here
        ttk.Label(dialog, text="תיאור הרשומה:").pack(pady=10)
        description_text = tk.Text(dialog, wrap="word", height=10)
        description_text.pack(fill="both", expand=True, padx=10, pady=10)
        description_text.insert("1.0", record.get("description", ""))
        description_text.configure(state="disabled")

        ttk.Button(dialog, text="סגור", command=dialog.destroy).pack(pady=10)

     except Exception as e:
        messagebox.showerror("שגיאה", f"שגיאה בטעינת הרשומה: {str(e)}")



    def create_stat_widget(self, parent, title, value, row, col):
        """יצירת ווידג'ט סטטיסטי"""
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=col, padx=10, pady=5)
        
        ttk.Label(
            frame,
            text=title,
            style="Main.TLabel"
        ).pack()
        
        ttk.Label(
            frame,
            text=value,
            style="Title.TLabel"
        ).pack()

    def create_doctors_table(self, parent):
     columns = ("name", "license", "spec", "email", "status", "reg_date")
    
     # הגדרת הטבלה עם אפשרות בחירה מרובה
     self.doctors_tree = ttk.Treeview(
        parent,
        columns=columns,
        show="headings",
        selectmode="browse"  # שינוי למצב בחירה בודד לצורך פשטות
     )
    
     # הגדרת הכותרות
     headers = {
        "name": "שם מלא",
        "license": "מספר רישיון",
        "spec": "התמחות",
        "email": "אימייל",
        "status": "סטטוס",
        "reg_date": "תאריך הרשמה"
     }
    
     # הגדרת העמודות
     for col in columns:
        self.doctors_tree.heading(col, text=headers[col])
        self.doctors_tree.column(col, width=100, anchor="center")
    
     # הוספת scrollbar
     scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.doctors_tree.yview)
     self.doctors_tree.configure(yscrollcommand=scrollbar.set)
    
     # מיקום הרכיבים
     self.doctors_tree.pack(side="left", fill="both", expand=True)
     scrollbar.pack(side="right", fill="y")
    
     # הוספת אירוע בחירה
     self.doctors_tree.bind('<<TreeviewSelect>>', self.on_doctor_select)
     
     # עדכון ראשוני של הרשימה
     self.update_doctors_list()


    def add_patient(self):
        """הוספת מטופל חדש"""
        dialog = tk.Toplevel(self.root)
        dialog.title("הוספת מטופל חדש")
        dialog.geometry("400x600")
        
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill="both", expand=True)
        
        fields = [
            ("שם מלא:", "name"),
            ("תעודת זהות:", "id_number"),
            ("גיל:", "age"),
            ("טלפון:", "phone"),
            ("כתובת:", "address"),
            ("היסטוריה רפואית:", "medical_history", True)
        ]
        
        entries = {}
        for label_text, field_name, *args in fields:
            field_frame = ttk.Frame(form_frame)
            field_frame.pack(fill="x", pady=5)
            
            ttk.Label(
                field_frame,
                text=label_text,
                style="Main.TLabel"
            ).pack(anchor="w")
            
            if args and args[0]:
                entry = tk.Text(field_frame, height=4)
            else:
                entry = ttk.Entry(field_frame, style="Main.TEntry")
            
            entry.pack(fill="x", pady=(2, 5))
            entries[field_name] = entry
        
        def submit():
                patient_data = {}
                for field_name, entry in entries.items():
                    if isinstance(entry, tk.Text):
                        value = entry.get("1.0", "end-1c").strip()
                    else:
                        value = entry.get().strip()
                    
                    if not value:
                        messagebox.showerror(
                            "שגיאה",
                            "נא למלא את כל השדות",
                            parent=dialog
                        )
                        return
                    
                    patient_data[field_name] = value
                
                try:
                    success = self.record_system.add_patient(
                        self.current_user["data"]["id"],
                        patient_data
                    )
                    
                    if success:
                        messagebox.showinfo(
                            "הצלחה",
                            "המטופל נוסף בהצלחה",
                            parent=dialog
                        )
                        dialog.destroy()
                        self.update_patients_list()
                    else:
                        messagebox.showerror(
                            "שגיאה",
                            "שגיאה בהוספת המטופל",
                            parent=dialog
                        )
                except Exception as e:
                    messagebox.showerror(
                        "שגיאה",
                        f"שגיאה בהוספת המטופל: {str(e)}",
                        parent=dialog
                    )
        
        # כפתורי פעולה
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.pack(fill="x", pady=20)
        
        ttk.Button(
            buttons_frame,
            text="הוסף",
            command=submit,
            style="Action.TButton"
        ).pack(side="right", padx=5)
        
        ttk.Button(
            buttons_frame,
            text="ביטול",
            command=dialog.destroy,
            style="Secondary.TButton"
        ).pack(side="right", padx=5)

    
    
    
    def view_patient(self):
        """צפייה בפרטי מטופל"""
        selection = self.patients_tree.selection()
        if not selection:
            messagebox.showwarning("אזהרה", "נא לבחור מטופל")
            return
        
        patient_id = self.patients_tree.item(selection[0])["values"][0]
        
        try:
            patients = self.record_system.get_doctor_patients(self.current_user["data"]["id"])
            patient = next((p for p in patients if p["id"] == patient_id), None)
            
            if not patient:
                messagebox.showerror("שגיאה", "מטופל לא נמצא")
                return
            
            dialog = tk.Toplevel(self.root)
            dialog.title(f"פרטי מטופל - {patient['name']}")
            dialog.geometry("800x600")
            
            main_frame = ttk.Frame(dialog, padding=20)
            main_frame.pack(fill="both", expand=True)
            
            # פרטים אישיים
            info_frame = ttk.LabelFrame(main_frame, text="פרטים אישיים")
            info_frame.pack(fill="x", pady=(0, 20))
            
            fields = [
                ("שם מלא:", "name"),
                ("תעודת זהות:", "id_number"),
                ("גיל:", "age"),
                ("טלפון:", "phone"),
                ("כתובת:", "address"),
                ("סטטוס:", "status"),
                ("ביקור אחרון:", "last_visit")
            ]
            
            for label_text, field_name in fields:
                field_frame = ttk.Frame(info_frame)
                field_frame.pack(fill="x", pady=5, padx=10)
                
                ttk.Label(
                    field_frame,
                    text=label_text,
                    style="Main.TLabel"
                ).pack(side="right")
                
                value = patient.get(field_name, "")
                if field_name == "last_visit" and value:
                    value = datetime.fromisoformat(value).strftime("%d/%m/%Y %H:%M")
                
                ttk.Label(
                    field_frame,
                    text=str(value),
                    style="Main.TLabel"
                ).pack(side="left")
            
            # היסטוריה רפואית
            history_frame = ttk.LabelFrame(main_frame, text="היסטוריה רפואית")
            history_frame.pack(fill="both", expand=True, pady=(0, 20))
            
            history_text = tk.Text(
                history_frame,
                wrap="word",
                height=4,
                state="disabled"
            )
            history_text.pack(fill="both", expand=True, padx=10, pady=10)
            
            history_text.configure(state="normal")
            history_text.delete("1.0", "end")
            history_text.insert("1.0", patient.get("medical_history", ""))
            history_text.configure(state="disabled")
            
            # רשומות רפואיות
            records_frame = ttk.LabelFrame(main_frame, text="רשומות רפואיות")
            records_frame.pack(fill="both", expand=True)
            
            records = self.record_system.get_patient_records(patient_id)
            
            records_tree = ttk.Treeview(
                records_frame,
                columns=("date", "type", "description"),
                show="headings"
            )
            
            records_tree.heading("date", text="תאריך")
            records_tree.heading("type", text="סוג")
            records_tree.heading("description", text="תיאור")
            
            records_tree.pack(fill="both", expand=True, padx=10, pady=10)
            
            for record in records:
                date = datetime.fromisoformat(record["creation_date"]).strftime("%d/%m/%Y %H:%M")
                records_tree.insert(
                    "",
                    "end",
                    values=(date, record["type"], record["description"])
                )
            
            # כפתורים
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.pack(fill="x", pady=20)
            
            ttk.Button(
                buttons_frame,
                text="הוסף רשומה",
                command=lambda: self.add_medical_record(patient_id, dialog),
                style="Action.TButton"
            ).pack(side="right", padx=5)
            
            ttk.Button(
                buttons_frame,
                text="סגור",
                command=dialog.destroy,
                style="Secondary.TButton"
            ).pack(side="right", padx=5)
            
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בטעינת פרטי המטופל: {str(e)}")


    def approve_selected_doctors(self):
     selection = self.doctors_tree.selection()  # Get selected doctors
     if not selection:
        messagebox.showwarning("אזהרה", "נא לבחור רופא לאישור")  # No selection warning
        return

     try:
        approved_count = 0
        for item in selection:
            # Get the doctor's details from the selected row
            doctor_values = self.doctors_tree.item(item)['values']
            
            if not doctor_values:
                continue

            license_number = doctor_values[1]  # Extract license number (second column)
            current_status = doctor_values[4]  # Extract current status (fifth column)

            # Check if the doctor is already approved
            if current_status == "מאושר":
                continue

            # Approve the doctor by license number
            if self.medical_system.approve_doctor(license_number):
                approved_count += 1
                print(f"Doctor with license {license_number} approved.")  # Log approved doctor

        # Notify the user of the result
        if approved_count > 0:
            messagebox.showinfo("הצלחה", f"{approved_count} רופאים אושרו בהצלחה")
            self.update_doctors_list()  # Refresh the list of doctors
        else:
            messagebox.showinfo("מידע", "לא נמצאו רופאים חדשים לאישור")
    
     except Exception as e:
        print(f"Error approving doctors: {str(e)}")  # Log the error
        messagebox.showerror("שגיאה", f"שגיאה באישור הרופאים: {str(e)}")

    
    
    def add_medical_record(self, patient_id, parent_window=None):
        """הוספת רשומה רפואית"""
        dialog = tk.Toplevel(parent_window or self.root)
        dialog.title("הוספת רשומה רפואית")
        dialog.geometry("500x400")
        
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill="both", expand=True)
        
        # סוג רשומה
        type_frame = ttk.Frame(form_frame)
        type_frame.pack(fill="x", pady=5)
        
        ttk.Label(
            type_frame,
            text="סוג רשומה:",
            style="Main.TLabel"
        ).pack(anchor="w")
        
        record_types = [
            "בדיקה רפואית",
            "מרשם תרופות",
            "הפניה למומחה",
            "תוצאות בדיקות",
            "אבחנה",
            "טיפול",
            "מעקב",
            "אחר"
        ]
        
        record_type = ttk.Combobox(
            type_frame,
            values=record_types,
            state="readonly"
        )
        record_type.pack(fill="x", pady=(2, 5))
        record_type.set(record_types[0])
        
        # תיאור
        description_frame = ttk.Frame(form_frame)
        description_frame.pack(fill="x", pady=5)
        
        ttk.Label(
            description_frame,
            text="תיאור:",
            style="Main.TLabel"
        ).pack(anchor="w")
        
        description_text = tk.Text(
            description_frame,
            height=10,
            width=40
        )
        description_text.pack(fill="both", expand=True, pady=(2, 5))
        
        def submit():
            record_data = {
                "type": record_type.get(),
                "description": description_text.get("1.0", "end-1c").strip()
            }
            
            if not record_data["description"]:
                messagebox.showerror(
                    "שגיאה",
                    "נא למלא תיאור",
                    parent=dialog
                )
                return
            
            try:
                success = self.record_system.add_medical_record(
                    self.current_user["data"]["id"],
                    patient_id,
                    record_data
                )
                
                if success:
                    messagebox.showinfo(
                        "הצלחה",
                        "הרשומה נוספה בהצלחה",
                        parent=dialog
                    )
                    dialog.destroy()
                    if parent_window:
                        parent_window.destroy()
                        self.view_patient()
                    self.update_records_list()
                else:
                    messagebox.showerror(
                        "שגיאה",
                        "שגיאה בהוספת הרשומה",
                        parent=dialog
                    )
            except Exception as e:
                messagebox.showerror(
                    "שגיאה",
                    f"שגיאה בהוספת הרשומה: {str(e)}",
                    parent=dialog
                )
        
        # כפתורי פעולה
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.pack(fill="x", pady=20)
        
        ttk.Button(
            buttons_frame,
            text="הוסף",
            command=submit,
            style="Action.TButton"
        ).pack(side="right", padx=5)
        
        ttk.Button(
            buttons_frame,
            text="ביטול",
            command=dialog.destroy,
            style="Secondary.TButton"
        ).pack(side="right", padx=5)
    def update_doctors_list(self):
     # ניקוי הטבלה
     for item in self.doctors_tree.get_children():
        self.doctors_tree.delete(item)
    
     try:
        doctors = self.medical_system.get_doctors()
        print(f"Loaded {len(doctors)} doctors")  # הדפסה לבדיקה
        
        for doctor_id, doctor in doctors.items():
            status = "מאושר" if doctor.get("is_approved", False) else "ממתין לאישור"
            reg_date = datetime.fromisoformat(doctor["registration_date"]).strftime("%d/%m/%Y")
            
            values = (
                doctor["name"],
                doctor.get("license", ""),
                doctor.get("specialization", ""),
                doctor["email"],
                status,
                reg_date
            )
            
            print(f"Inserting doctor: {values}")  # הדפסה לבדיקה
            self.doctors_tree.insert("", "end", values=values)
            
     except Exception as e:
        print(f"Error updating list: {str(e)}")  # הדפסה לבדיקה
        messagebox.showerror("שגיאה", f"שגיאה בטעינת רשימת הרופאים: {str(e)}")
    

    
    def update_patients_list(self):
        """עדכון רשימת המטופלים"""
        for item in self.patients_tree.get_children():
            self.patients_tree.delete(item)
        
        try:
            patients = self.record_system.get_doctor_patients(
                self.current_user["data"]["id"]
            )
            
            for patient in patients:
                last_visit = (
                    datetime.fromisoformat(patient["last_visit"]).strftime("%d/%m/%Y")
                    if patient.get("last_visit")
                    else "טרם ביקר"
                )
                
                self.patients_tree.insert(
                    "",
                    "end",
                    values=(
                        patient["id"],
                        patient["name"],
                        patient["age"],
                        last_visit,
                        patient["status"]
                    )
                )
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בטעינת רשימת המטופלים: {str(e)}")
    
    def on_doctor_select(self, event):
     selection = self.doctors_tree.selection()
     if selection:
        # הדפסה לבדיקה
        print(f"נבחר רופא: {self.doctors_tree.item(selection[0])['values']}")


   
    def update_records_list(self):
        """עדכון רשימת הרשומות הרפואיות"""
        for item in self.records_tree.get_children():
            self.records_tree.delete(item)
        
        try:
            records = self.record_system.get_doctor_records(
                self.current_user["data"]["id"]
            )
            
            for record in records:
                date = datetime.fromisoformat(record["creation_date"]).strftime("%d/%m/%Y %H:%M")
                patient = record.get("patient_name", "לא ידוע")
                
                self.records_tree.insert(
                    "",
                    "end",
                    values=(
                        patient,
                        date,
                        record["type"],
                        record["description"][:50] + "..." if len(record["description"]) > 50 else record["description"]
                    )
                )
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בטעינת רשימת הרשומות: {str(e)}")

def main():
    """הפעלת המערכת"""
    try:
        app = MedicalGUI()
        app.run()
    except Exception as e:
        messagebox.showerror("שגיאה קריטית", f"שגיאה בהפעלת המערכת: {str(e)}")

if __name__ == "__main__":
    main()
