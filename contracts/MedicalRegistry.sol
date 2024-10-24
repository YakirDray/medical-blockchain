// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MedicalRegistry {
    struct Doctor {
        string name;
        string specialization;
        string licenseNumber;
        bool isRegistered;
        bool isApproved;
        mapping(address => bool) patients;
        address[] patientList;
        uint256 patientCount;
        string email;
        uint256 registrationDate;
    }
    
    struct Patient {
        string name;
        uint256 age;
        bool exists;
        string medicalId;
        address doctorAddress;
        uint256 registrationDate;
    }
    
    address public admin;
    mapping(address => Doctor) public doctors;
    mapping(address => Patient) public patients;
    mapping(string => bool) public usedLicenseNumbers;
    mapping(string => bool) public usedEmails;
    address[] public doctorAddresses;
    
    event DoctorRegistered(address indexed doctorAddress, string name);
    event PatientRegistered(address indexed patientAddress, string name, address indexed doctorAddress);
    event DoctorApproved(address indexed doctorAddress);
    event DoctorRejected(address indexed doctorAddress, string reason);
    
    constructor() {
        admin = msg.sender;
    }
    
    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can perform this action");
        _;
    }
    
    modifier onlyRegisteredAndApproved() {
        require(doctors[msg.sender].isRegistered && doctors[msg.sender].isApproved, 
                "Only registered and approved doctors can perform this action");
        _;
    }
    
    function registerDoctor(
        address _doctorAddress,
        string memory _name, 
        string memory _specialization,
        string memory _licenseNumber,
        string memory _email
    ) public onlyAdmin {
        require(!doctors[_doctorAddress].isRegistered, "Doctor already registered");
        require(!usedLicenseNumbers[_licenseNumber], "License number already in use");
        require(!usedEmails[_email], "Email already in use");
        
        Doctor storage newDoctor = doctors[_doctorAddress];
        newDoctor.name = _name;
        newDoctor.specialization = _specialization;
        newDoctor.licenseNumber = _licenseNumber;
        newDoctor.email = _email;
        newDoctor.isRegistered = true;
        newDoctor.isApproved = false;
        newDoctor.patientCount = 0;
        newDoctor.registrationDate = block.timestamp;
        
        usedLicenseNumbers[_licenseNumber] = true;
        usedEmails[_email] = true;
        doctorAddresses.push(_doctorAddress);
        
        emit DoctorRegistered(_doctorAddress, _name);
    }
    
    function approveDoctor(address _doctorAddress) public onlyAdmin {
        require(doctors[_doctorAddress].isRegistered, "Doctor not registered");
        require(!doctors[_doctorAddress].isApproved, "Doctor already approved");
        
        doctors[_doctorAddress].isApproved = true;
        emit DoctorApproved(_doctorAddress);
    }
    
    function registerPatient(
        address _patientAddress,
        string memory _name,
        uint256 _age,
        string memory _medicalId
    ) public onlyRegisteredAndApproved {
        require(!patients[_patientAddress].exists, "Patient already registered");
        
        patients[_patientAddress] = Patient({
            name: _name,
            age: _age,
            exists: true,
            medicalId: _medicalId,
            doctorAddress: msg.sender,
            registrationDate: block.timestamp
        });
        
        doctors[msg.sender].patients[_patientAddress] = true;
        doctors[msg.sender].patientList.push(_patientAddress);
        doctors[msg.sender].patientCount++;
        
        emit PatientRegistered(_patientAddress, _name, msg.sender);
    }
    
    function getDoctorPatients(address _doctorAddress) public view returns (address[] memory) {
        require(msg.sender == admin || msg.sender == _doctorAddress, 
                "Only admin or the doctor can view their patients");
        return doctors[_doctorAddress].patientList;
    }
    
    function getAllDoctors() public view returns (address[] memory) {
        return doctorAddresses;
    }
    
    function getDoctorDetails(address _doctorAddress) public view returns (
        string memory name,
        string memory specialization,
        string memory licenseNumber,
        bool isRegistered,
        bool isApproved,
        uint256 patientCount,
        string memory email,
        uint256 registrationDate
    ) {
        Doctor storage doctor = doctors[_doctorAddress];
        return (
            doctor.name,
            doctor.specialization,
            doctor.licenseNumber,
            doctor.isRegistered,
            doctor.isApproved,
            doctor.patientCount,
            doctor.email,
            doctor.registrationDate
        );
    }
    
    function getPatientDetails(address _patientAddress) public view returns (
        string memory name,
        uint256 age,
        string memory medicalId,
        address doctorAddress,
        uint256 registrationDate
    ) {
        require(msg.sender == admin || 
                msg.sender == patients[_patientAddress].doctorAddress,
                "Only admin or patient's doctor can view details");
        
        Patient storage patient = patients[_patientAddress];
        return (
            patient.name,
            patient.age,
            patient.medicalId,
            patient.doctorAddress,
            patient.registrationDate
        );
    }
}