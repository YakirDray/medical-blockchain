import json
import os
from datetime import datetime
import uuid
from typing import Dict, Any

class MedicalSystem:
    def __init__(self):
        """אתחול המערכת הרפואית"""
        self.doctors: Dict[str, Any] = {}
        self.doctors_file = 'doctors.json'
        self.load_doctors()

    def load_doctors(self) -> None:
        """טעינת רשימת הרופאים מהקובץ"""
        try:
            if os.path.exists(self.doctors_file):
                with open(self.doctors_file, 'r', encoding='utf-8') as f:
                    self.doctors = json.load(f)
            else:
                self.doctors = {}
                self.save_doctors()  # יצירת קובץ ריק
        except Exception as e:
            print(f"Error loading doctors: {str(e)}")
            self.doctors = {}

    def save_doctors(self) -> None:
        """שמירת רשימת הרופאים לקובץ"""
        try:
            with open(self.doctors_file, 'w', encoding='utf-8') as f:
                json.dump(self.doctors, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving doctors: {str(e)}")

    def register_doctor(self, data: Dict[str, Any]) -> bool:
        """
        רישום רופא חדש
        
        Args:
            data: מילון עם פרטי הרופא
                {
                    "name": str - שם מלא,
                    "specialization": str - התמחות,
                    "license": str - מספר רישיון,
                    "email": str - אימייל,
                    "private_key": str - סיסמה מוצפנת
                }
        Returns:
            bool: האם הרישום הצליח
        """
        try:
            # בדיקה אם האימייל כבר קיים במערכת
            for doc in self.doctors.values():
                if doc['email'] == data['email']:
                    print("Email already exists")
                    return False
                
            # בדיקה אם מספר הרישיון כבר קיים
            for doc in self.doctors.values():
                if doc['license_number'] == data['license']:
                    print("License number already exists")
                    return False

            # יצירת מזהה ייחודי
            doctor_id = str(uuid.uuid4())
            
            # יצירת רשומת הרופא
            doctor_record = {
                "name": data["name"],
                "specialization": data["specialization"],
                "license_number": data["license"],
                "email": data["email"],
                "private_key": data["private_key"],
                "is_approved": False,
                "registration_date": datetime.now().isoformat(),
                "last_login": None,
                "active": True
            }
            
            # הוספה למילון הרופאים
            self.doctors[doctor_id] = doctor_record
            
            # שמירה לקובץ
            self.save_doctors()
            
            return True
            
        except Exception as e:
            print(f"Error registering doctor: {str(e)}")
            return False

    def get_doctors(self) -> Dict[str, Any]:
        """קבלת רשימת הרופאים"""
        return self.doctors

    def approve_doctor(self, license_number: str) -> bool:
        """
        אישור רופא
        
        Args:
            license_number: מספר רישיון הרופא
            
        Returns:
            bool: האם האישור הצליח
        """
        try:
            for doctor in self.doctors.values():
                if doctor["license_number"] == license_number:
                    doctor["is_approved"] = True
                    doctor["approval_date"] = datetime.now().isoformat()
                    self.save_doctors()
                    return True
            return False
        except Exception as e:
            print(f"Error approving doctor: {str(e)}")
            return False

    def get_system_stats(self) -> Dict[str, int]:
        """
        קבלת סטטיסטיקות מערכת
        
        Returns:
            Dict[str, int]: מילון עם הנתונים הסטטיסטיים
        """
        try:
            return {
                "total_doctors": len(self.doctors),
                "pending_doctors": sum(1 for d in self.doctors.values() if not d["is_approved"]),
                "active_doctors": sum(1 for d in self.doctors.values() if d["is_approved"] and d.get("active", True)),
                "active_patients": 0,  # TODO: להשלים כשתהיה מערכת מטופלים
                "total_records": 0     # TODO: להשלים כשתהיה מערכת רשומות
            }
        except Exception as e:
            print(f"Error getting system stats: {str(e)}")
            return {
                "total_doctors": 0,
                "pending_doctors": 0,
                "active_doctors": 0,
                "active_patients": 0,
                "total_records": 0
            }

    def update_doctor_login(self, email: str) -> bool:
        """
        עדכון תאריך התחברות אחרון של רופא
        
        Args:
            email: אימייל הרופא
            
        Returns:
            bool: האם העדכון הצליח
        """
        try:
            for doctor in self.doctors.values():
                if doctor["email"] == email:
                    doctor["last_login"] = datetime.now().isoformat()
                    self.save_doctors()
                    return True
            return False
        except Exception as e:
            print(f"Error updating doctor login: {str(e)}")
            return False

    def deactivate_doctor(self, license_number: str) -> bool:
        """
        השבתת חשבון רופא
        
        Args:
            license_number: מספר רישיון הרופא
            
        Returns:
            bool: האם ההשבתה הצליחה
        """
        try:
            for doctor in self.doctors.values():
                if doctor["license_number"] == license_number:
                    doctor["active"] = False
                    doctor["deactivation_date"] = datetime.now().isoformat()
                    self.save_doctors()
                    return True
            return False
        except Exception as e:
            print(f"Error deactivating doctor: {str(e)}")
            return False