import json
import os
from datetime import datetime
from collections import defaultdict

class MedicalAnalytics:
    def __init__(self):
        print("מאתחל מערכת ניתוח נתונים...")
        self._load_data()
    
    def _load_data(self):
        """טעינת כל הנתונים"""
        try:
            # טעינת מטופלים
            if os.path.exists('patients.json'):
                with open('patients.json', 'r') as f:
                    self.patients = json.load(f)
            else:
                self.patients = {}
            
            # טעינת רופאים
            if os.path.exists('doctors.json'):
                with open('doctors.json', 'r') as f:
                    self.doctors = json.load(f)
            else:
                self.doctors = {}
            
        except Exception as e:
            print(f"שגיאה בטעינת נתונים: {str(e)}")
            self.patients = {}
            self.doctors = {}
    
    def _load_patient_records(self, patient_id):
        """טעינת רשומות של מטופל ספציפי"""
        try:
            filename = f'medical_records_{patient_id}.json'
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"שגיאה בטעינת רשומות מטופל: {str(e)}")
            return []
    
    def _calculate_average(self, numbers):
        """חישוב ממוצע פשוט"""
        valid_numbers = [n for n in numbers if isinstance(n, (int, float))]
        if not valid_numbers:
            return 0
        return sum(valid_numbers) / len(valid_numbers)
    
    def get_patient_statistics(self, patient_address):
        """ניתוח נתוני מטופל"""
        try:
            if patient_address not in self.patients:
                raise ValueError("מטופל לא קיים במערכת")
            
            patient = self.patients[patient_address]
            records = self._load_patient_records(patient['medical_id'])
            
            if not records:
                print(f"אין רשומות רפואיות למטופל {patient['name']}")
                return None
            
            # איסוף נתונים
            pulses = []
            weights = []
            blood_pressures = []
            visit_types = defaultdict(int)
            
            for record in records:
                data = record['data']
                
                # איסוף נתונים מספריים
                if 'דופק' in data:
                    try:
                        pulses.append(float(data['דופק']))
                    except (ValueError, TypeError):
                        pass
                
                if 'משקל' in data:
                    try:
                        weights.append(float(data['משקל']))
                    except (ValueError, TypeError):
                        pass
                
                if 'לחץ דם' in data:
                    blood_pressures.append(data['לחץ דם'])
                
                if 'סוג ביקור' in data:
                    visit_types[data['סוג ביקור']] += 1
            
            # חישוב סטטיסטיקות
            stats = {
                'שם': patient['name'],
                'מספר ביקורים': len(records),
                'ביקור ראשון': records[0]['timestamp'] if records else None,
                'ביקור אחרון': records[-1]['timestamp'] if records else None,
                'דופק ממוצע': self._calculate_average(pulses),
                'משקל ממוצע': self._calculate_average(weights),
                'סוגי ביקורים': dict(visit_types)
            }
            
            # הדפסת הסטטיסטיקות
            self._print_patient_stats(stats)
            
            return stats
            
        except Exception as e:
            print(f"❌ שגיאה בניתוח נתוני מטופל: {str(e)}")
            return None
    
    def _print_patient_stats(self, stats):
        """הדפסת סטטיסטיקות מטופל"""
        print(f"\nסטטיסטיקות עבור {stats['שם']}:")
        print(f"מספר ביקורים כולל: {stats['מספר ביקורים']}")
        print(f"ביקור ראשון: {stats['ביקור ראשון']}")
        print(f"ביקור אחרון: {stats['ביקור אחרון']}")
        
        if stats['דופק ממוצע']:
            print(f"דופק ממוצע: {stats['דופק ממוצע']:.1f}")
        
        if stats['משקל ממוצע']:
            print(f"משקל ממוצע: {stats['משקל ממוצע']:.1f} ק\"ג")
        
        print("\nהתפלגות סוגי ביקורים:")
        for visit_type, count in stats['סוגי ביקורים'].items():
            print(f"  {visit_type}: {count}")
    
    def get_system_statistics(self):
        """סטטיסטיקות כלליות של המערכת"""
        try:
            # נתונים בסיסיים
            total_patients = len(self.patients)
            total_doctors = len(self.doctors)
            
            # ספירת ביקורים
            visits_by_doctor = defaultdict(int)
            total_visits = 0
            
            # עיבוד כל הרשומות
            for patient in self.patients.values():
                records = self._load_patient_records(patient['medical_id'])
                total_visits += len(records)
                
                for record in records:
                    if 'doctor' in record:
                        visits_by_doctor[record['doctor']] += 1
            
            # חישוב סטטיסטיקות
            stats = {
                'מספר מטופלים': total_patients,
                'מספר רופאים': total_doctors,
                'מספר ביקורים כולל': total_visits,
                'ממוצע ביקורים למטופל': total_visits / total_patients if total_patients else 0,
                'ביקורים לפי רופא': dict(visits_by_doctor)
            }
            
            # הדפסת הסטטיסטיקות
            self._print_system_stats(stats)
            
            return stats
            
        except Exception as e:
            print(f"❌ שגיאה בחישוב סטטיסטיקות מערכת: {str(e)}")
            return None
    
    def _print_system_stats(self, stats):
        """הדפסת סטטיסטיקות מערכת"""
        print("\nסטטיסטיקות מערכת:")
        print(f"מספר מטופלים: {stats['מספר מטופלים']}")
        print(f"מספר רופאים: {stats['מספר רופאים']}")
        print(f"מספר ביקורים כולל: {stats['מספר ביקורים כולל']}")
        print(f"ממוצע ביקורים למטופל: {stats['ממוצע ביקורים למטופל']:.1f}")
        
        if stats['ביקורים לפי רופא']:
            print("\nביקורים לפי רופא:")
            for doctor, visits in stats['ביקורים לפי רופא'].items():
                doctor_name = self.doctors.get(doctor, {}).get('name', 'לא ידוע')
                print(f"  {doctor_name}: {visits} ביקורים")