import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from web3 import Web3
from datetime import datetime

class MedicalInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Decentralized Medical System")
        self.root.geometry("1024x768")

        # Blockchain connection
        self.w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
        if not self.w3.is_connected():
            messagebox.showerror("Error", "Cannot connect to blockchain")
            raise Exception("No blockchain connection")

        # Contract loading
        self.load_contract()
        
        # Admin account
        self.admin_account = self.w3.eth.accounts[0]
        
        # Setup styles
        self.setup_styles()
        
        # Create login screen
        self.create_login_screen()

    def setup_styles(self):
        """Setup GUI styles"""
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Helvetica', 16, 'bold'))
        style.configure('Header.TLabel', font=('Helvetica', 14, 'bold'))
        style.configure('Info.TLabel', font=('Helvetica', 10))

    def load_contract(self):
        """Load smart contract"""
        try:
            # Read ABI and contract address
            with open('contracts/contract_abi.json', 'r') as f:
                contract_abi = json.load(f)
            with open('contracts/contract_address.txt', 'r') as f:
                contract_address = f.read().strip()

            # Create contract object
            self.contract = self.w3.eth.contract(
                address=contract_address,
                abi=contract_abi
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error loading contract: {str(e)}")
            raise

    def create_login_screen(self):
        """Create login screen"""
        self.clear_screen()
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(expand=True)
        
        # Title
        ttk.Label(main_frame, 
                 text="Decentralized Medical System", 
                 style='Title.TLabel').pack(pady=20)
        
        # Wallet address field
        ttk.Label(main_frame, text="Wallet Address:").pack(pady=5)
        self.wallet_address_entry = ttk.Entry(main_frame, width=50)
        self.wallet_address_entry.pack(pady=5)
        
        # User type selection
        user_frame = ttk.Frame(main_frame)
        user_frame.pack(pady=10)
        
        self.user_type = tk.StringVar(value="doctor")
        ttk.Radiobutton(user_frame, 
                       text="Doctor",
                       variable=self.user_type,
                       value="doctor").pack(side='left', padx=10)
        ttk.Radiobutton(user_frame,
                       text="Admin",
                       variable=self.user_type,
                       value="admin").pack(side='left', padx=10)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame,
                  text="Login",
                  command=self.handle_login).pack(side='left', padx=5)
        ttk.Button(button_frame,
                  text="Doctor Registration",
                  command=self.show_doctor_registration).pack(side='left', padx=5)

    def handle_login(self):
        """Handle login process"""
        try:
            address = self.wallet_address_entry.get().strip()
            if not Web3.is_address(address):
                raise ValueError("Invalid wallet address")

            if self.user_type.get() == "admin":
                if address.lower() == self.admin_account.lower():
                    self.show_admin_dashboard()
                else:
                    raise ValueError("Unauthorized address for admin")
            else:
                # Check doctor
                doctor_details = self.contract.functions.getDoctorDetails(address).call()
                if not doctor_details[3]:  # isRegistered
                    raise ValueError("Doctor not registered in the system")
                if not doctor_details[4]:  # isApproved
                    raise ValueError("Doctor account not yet approved")
                
                # Save current account
                self.current_doctor_address = address
                self.show_doctor_dashboard(address, doctor_details)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_doctor_dashboard(self, doctor_address, doctor_details):
        """Show doctor dashboard"""
        self.clear_screen()
        
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Doctor info
        ttk.Label(main_frame, 
                 text=f"Welcome, Dr. {doctor_details[0]}", 
                 style='Title.TLabel').pack(pady=10)
             
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill='x', pady=10)
        
        # Display doctor details
        ttk.Label(info_frame,
                 text=f"Specialization: {doctor_details[1]}",
                 style='Info.TLabel').pack(side='left', padx=10)
        ttk.Label(info_frame,
                 text=f"License Number: {doctor_details[2]}",
                 style='Info.TLabel').pack(side='left', padx=10)
        ttk.Label(info_frame,
                 text=f"Wallet Address: {doctor_address}",
                 style='Info.TLabel').pack(side='left', padx=10)

        # Patients table
        self.create_patients_table(main_frame)

        # Add patient form
        self.create_add_patient_form(main_frame)

        # Initial patients list load
        self.refresh_patients_list()

    def create_patients_table(self, parent_frame):
        """Create patients table"""
        patients_frame = ttk.LabelFrame(parent_frame, text="Patients List", padding="10")
        patients_frame.pack(fill='both', expand=True, pady=10)
        
        columns = ('Address', 'Name', 'Age', 'Medical ID', 'Registration Date')
        self.patients_tree = ttk.Treeview(patients_frame, 
                                        columns=columns, 
                                        show='headings',
                                        height=10)
        
        for col in columns:
            self.patients_tree.heading(col, text=col)
            self.patients_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(patients_frame, 
                                orient=tk.VERTICAL,
                                command=self.patients_tree.yview)
        self.patients_tree.configure(yscrollcommand=scrollbar.set)
        
        self.patients_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def create_add_patient_form(self, parent_frame):
        """Create add patient form"""
        add_frame = ttk.LabelFrame(parent_frame, text="Add New Patient", padding="10")
        add_frame.pack(fill='x', pady=10)
        
        fields_frame = ttk.Frame(add_frame)
        fields_frame.pack(fill='x', pady=5)
        
        self.patient_entries = {}
        fields = [
            ("Wallet Address:", "wallet", 40),
            ("Full Name:", "name", 30),
            ("Age:", "age", 5),
            ("Medical ID:", "medical_id", 15)
        ]
        
        for label, field, width in fields:
            field_frame = ttk.Frame(fields_frame)
            field_frame.pack(side='left', padx=5)
            
            ttk.Label(field_frame, text=label).pack(anchor='w')
            entry = ttk.Entry(field_frame, width=width)
            entry.pack()
            self.patient_entries[field] = entry

        buttons_frame = ttk.Frame(add_frame)
        buttons_frame.pack(fill='x', pady=10)
        
        ttk.Button(buttons_frame, 
                  text="Add Patient",
                  command=self.add_new_patient).pack(side='left', padx=5)
        ttk.Button(buttons_frame, 
                  text="Refresh List",
                  command=self.refresh_patients_list).pack(side='left', padx=5)
        ttk.Button(buttons_frame, 
                  text="Logout",
                  command=self.create_login_screen).pack(side='left', padx=5)

    def show_admin_dashboard(self):
        """Show admin dashboard"""
        self.clear_screen()
        
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="System Administration",
                 style='Title.TLabel').pack(pady=20)
        
        # Doctors table
        columns = ('Address', 'Name', 'Specialization', 'License Number', 'Status')
        self.doctors_tree = ttk.Treeview(main_frame, columns=columns, show='headings')
        
        for col in columns:
            self.doctors_tree.heading(col, text=col)
            self.doctors_tree.column(col, width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL,
                                command=self.doctors_tree.yview)
        self.doctors_tree.configure(yscrollcommand=scrollbar.set)
        
        self.doctors_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Approve Doctor",
                  command=self.approve_selected_doctor).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Refresh List",
                  command=self.refresh_doctors_list).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Logout",
                  command=self.create_login_screen).pack(side='left', padx=5)
        
        self.refresh_doctors_list()

    def show_doctor_registration(self):
        """Show doctor registration form"""
        reg_window = tk.Toplevel(self.root)
        reg_window.title("New Doctor Registration")
        reg_window.geometry("500x600")
        
        frame = ttk.Frame(reg_window, padding="20")
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="Doctor Registration",
                 style='Header.TLabel').pack(pady=10)
        
        fields = [
            ("Wallet Address:", "wallet"),
            ("Full Name:", "name"),
            ("Specialization:", "specialization"),
            ("License Number:", "license"),
            ("Email:", "email")
        ]
        
        entries = {}
        for label, field in fields:
            ttk.Label(frame, text=label).pack(anchor='w')
            entry = ttk.Entry(frame, width=40)
            entry.pack(pady=5)
            entries[field] = entry
            
        def register():
            try:
                wallet = entries['wallet'].get().strip()
                if not Web3.is_address(wallet):
                    raise ValueError("Invalid wallet address")
                    
                if not all(entries[f].get().strip() for f in ['name', 'specialization', 'license', 'email']):
                    raise ValueError("All fields must be filled")
                
                tx_hash = self.contract.functions.registerDoctor(
                    wallet,
                    entries['name'].get().strip(),
                    entries['specialization'].get().strip(),
                    entries['license'].get().strip(),
                    entries['email'].get().strip()
                ).transact({'from': self.admin_account})
                
                self.w3.eth.wait_for_transaction_receipt(tx_hash)
                
                messagebox.showinfo("Success", "Registration successful! Waiting for admin approval")
                reg_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", str(e))
                
        ttk.Button(frame, text="Register", command=register).pack(pady=20)

    def refresh_patients_list(self):
        """Refresh patients list"""
        try:
            # Clear table
            for item in self.patients_tree.get_children():
                self.patients_tree.delete(item)

            # Get patients list
            patients = self.contract.functions.getDoctorPatients(
                self.current_doctor_address
            ).call({
                'from': self.current_doctor_address
            })

            # Display patients
            for patient_address in patients:
                try:
                    details = self.contract.functions.getPatientDetails(
                        patient_address
                    ).call({
                        'from': self.current_doctor_address
                    })
                    
                    # Convert timestamp
                    registration_date = datetime.fromtimestamp(
                        details[4]
                    ).strftime('%Y-%m-%d %H:%M')
                    
                    # Add to table
                    self.patients_tree.insert('', 'end', values=(
                        patient_address,
                        details[0],  # name
                        details[1],  # age
                        details[2],  # medicalId
                        registration_date
                    ))
                except Exception as e:
                    print(f"Error loading patient details {patient_address}: {str(e)}")
                    continue
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error loading patients list: {str(e)}")

    def refresh_doctors_list(self):
        """Refresh doctors list"""
        try:
            # Clear table
            for item in self.doctors_tree.get_children():
                self.doctors_tree.delete(item)

            # Get doctors list
            doctors = self.contract.functions.getAllDoctors().call()
            
            # Display doctors
            for address in doctors:
                details = self.contract.functions.getDoctorDetails(address).call()
                status = "Approved" if details[4] else "Pending Approval"
                
                self.doctors_tree.insert('', 'end', values=(
                    address,
                    details[0],  # name
                    details[1],  # specialization
                    details[2],  # licenseNumber
                    status
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading doctors list: {str(e)}")

    def add_new_patient(self):
        """Add new patient"""
        try:
            # Input validation
            wallet = self.patient_entries['wallet'].get().strip()
            if not Web3.is_address(wallet):
                raise ValueError("Invalid wallet address")
            
            age = self.patient_entries['age'].get().strip()
            if not age.isdigit() or int(age) <= 0:
                raise ValueError("Age must be a positive number")
            
            name = self.patient_entries['name'].get().strip()
            medical_id = self.patient_entries['medical_id'].get().strip()
            
            if not all([name, medical_id]):
                raise ValueError("All fields must be filled")

            # Send transaction
            tx_hash = self.contract.functions.registerPatient(
                wallet,
                name,
                int(age),
                medical_id
            ).transact({
                'from': self.current_doctor_address,
                'gas': 300000
            })
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                messagebox.showinfo("Success", "Patient added successfully")
                
                # Clear fields
                for entry in self.patient_entries.values():
                    entry.delete(0, tk.END)
                    
                # Refresh list
                self.refresh_patients_list()
            else:
                raise Exception("Transaction failed")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error adding patient: {str(e)}")

    def approve_selected_doctor(self):
        """Approve selected doctor"""
        try:
            selected = self.doctors_tree.selection()
            if not selected:
                raise ValueError("Please select a doctor from the list")
            
            doctor_address = self.doctors_tree.item(selected[0])['values'][0]
            
            # Send approval transaction
            tx_hash = self.contract.functions.approveDoctor(
                doctor_address
            ).transact({
                'from': self.admin_account,
                'gas': 200000
            })
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                messagebox.showinfo("Success", "Doctor approved successfully")
                self.refresh_doctors_list()
            else:
                raise Exception("Transaction failed")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error approving doctor: {str(e)}")

    def clear_screen(self):
        """Clear screen"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def run(self):
        """Run application"""
        self.root.mainloop()

def main():
    """Main function"""
    try:
        app = MedicalInterface()
        app.run()
    except Exception as e:
        print(f"System error: {str(e)}")
        raise

if __name__ == "__main__":
    main()