import json
import os
from datetime import datetime
import bcrypt

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def write_json(filename, data):
    path = os.path.join(DATA_DIR, filename)
    key = filename.replace(".json", "")
    with open(path, "w") as f:
        json.dump({key: data}, f, indent=2)


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


users = [
    {"id": "USR001", "name": "Admin User", "email": "admin@hms.com", "password": hash_password("admin123"), "role": "admin", "createdAt": "2026-08-12T00:00:00"},
    {"id": "USR002", "name": "Dr. Sarah Johnson", "email": "doctor@hms.com", "password": hash_password("doctor123"), "role": "doctor", "createdAt": "2026-08-12T00:00:00"},
    {"id": "USR003", "name": "John Patient", "email": "patient@hms.com", "password": hash_password("patient123"), "role": "patient", "createdAt": "2026-08-12T00:00:00"},
    {"id": "USR004", "name": "Receptionist", "email": "reception@hms.com", "password": hash_password("reception123"), "role": "receptionist", "createdAt": "2026-08-12T00:00:00"},
    {"id": "USR005", "name": "Pharmacist", "email": "pharmacy@hms.com", "password": hash_password("pharmacy123"), "role": "pharmacist", "createdAt": "2026-08-12T00:00:00"},
]

doctors = [
    {"id": "DOC001", "doctorId": "DOCA1B2C3", "name": "Dr. Sarah Johnson", "specialization": "Cardiology", "phone": "555-0101", "email": "sarah.johnson@hms.com", "department": "Cardiology", "availability": "Mon-Fri 9AM-5PM", "createdAt": "2026-08-12T00:00:00", "updatedAt": "2026-08-12T00:00:00"},
    {"id": "DOC002", "doctorId": "DOCD4E5F6", "name": "Dr. Michael Lee", "specialization": "Neurology", "phone": "555-0102", "email": "michael.lee@hms.com", "department": "Neurology", "availability": "Mon-Fri 10AM-6PM", "createdAt": "2026-08-12T00:00:00", "updatedAt": "2026-08-12T00:00:00"},
    {"id": "DOC003", "doctorId": "DOGG7H8I9", "name": "Dr. Emily Davis", "specialization": "Pediatrics", "phone": "555-0103", "email": "emily.davis@hms.com", "department": "Pediatrics", "availability": "Tue-Sat 8AM-4PM", "createdAt": "2026-08-12T00:00:00", "updatedAt": "2026-08-12T00:00:00"},
    {"id": "DOC004", "doctorId": "DOCJ0K1L2", "name": "Dr. James Wilson", "specialization": "Orthopedics", "phone": "555-0104", "email": "james.wilson@hms.com", "department": "Orthopedics", "availability": "Mon-Fri 9AM-5PM", "createdAt": "2026-08-12T00:00:00", "updatedAt": "2026-08-12T00:00:00"},
]

patients = [
    {"id": "PAT001", "patientId": "PATX9Y8Z7", "name": "John Patient", "age": 34, "gender": "Male", "phone": "555-1001", "email": "john.patient@email.com", "address": "123 Main St", "bloodGroup": "O+", "emergencyContact": "555-2001", "createdAt": "2026-08-12T00:00:00", "updatedAt": "2026-08-12T00:00:00"},
    {"id": "PAT002", "patientId": "PATW6V5U4", "name": "Alice Smith", "age": 28, "gender": "Female", "phone": "555-1002", "email": "alice.smith@email.com", "address": "456 Oak Ave", "bloodGroup": "A-", "emergencyContact": "555-2002", "createdAt": "2026-08-12T00:00:00", "updatedAt": "2026-08-12T00:00:00"},
    {"id": "PAT003", "patientId": "PATT3S2R1", "name": "Bob Brown", "age": 45, "gender": "Male", "phone": "555-1003", "email": "bob.brown@email.com", "address": "789 Pine Rd", "bloodGroup": "B+", "emergencyContact": "555-2003", "createdAt": "2026-08-12T00:00:00", "updatedAt": "2026-08-12T00:00:00"},
]

today = datetime.utcnow().strftime("%Y-%m-%d")
appointments = [
    {"id": "APT001", "appointmentId": "APTQ1W2E3", "patientId": "PAT001", "doctorId": "DOC001", "date": today, "time": "09:00", "reason": "Chest pain follow-up", "status": "Scheduled", "createdAt": "2026-08-12T00:00:00", "updatedAt": "2026-08-12T00:00:00"},
    {"id": "APT002", "appointmentId": "APTR4T5Y6", "patientId": "PAT002", "doctorId": "DOC002", "date": today, "time": "10:30", "reason": "Migraine checkup", "status": "Confirmed", "createdAt": "2026-08-12T00:00:00", "updatedAt": "2026-08-12T00:00:00"},
    {"id": "APT003", "appointmentId": "APTU7I8O9", "patientId": "PAT003", "doctorId": "DOC003", "date": today, "time": "11:00", "reason": "Child vaccination", "status": "Scheduled", "createdAt": "2026-08-12T00:00:00", "updatedAt": "2026-08-12T00:00:00"},
]

write_json("users.json", users)
write_json("doctors.json", doctors)
write_json("patients.json", patients)
write_json("appointments.json", appointments)
write_json("auditLogs.json", [])

print("Seed data created successfully!")
