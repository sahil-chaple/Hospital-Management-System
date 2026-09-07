from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime, timedelta
from jose import JWTError, jwt
import json
import os
import uuid
import bcrypt

app = FastAPI(title="Hospital Management System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "hms_secret_key_2026_super_secure_change_in_production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f).get(filename.replace(".json", ""), [])


def save_json(filename, data):
    path = os.path.join(DATA_DIR, filename)
    key = filename.replace(".json", "")
    with open(path, "w") as f:
        json.dump({key: data}, f, indent=2)


def log_audit(user_id: str, action: str):
    logs = load_json("auditLogs.json")
    logs.append({
        "id": f"LOG{str(uuid.uuid4())[:8].upper()}",
        "userId": user_id,
        "action": action,
        "timestamp": datetime.utcnow().isoformat()
    })
    save_json("auditLogs.json", logs)


def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    users = load_json("users.json")
    user = next((u for u in users if u["email"] == email), None)
    if user is None:
        raise credentials_exception
    return user


def require_roles(*roles):
    async def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return current_user
    return role_checker


# --- Models ---

class UserRegister(BaseModel):
    name: str
    email: str
    password: str
    role: str = "patient"

    @validator("email")
    def validate_email(cls, v):
        if "@" not in v:
            raise ValueError("Invalid email")
        return v

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v

    @validator("role")
    def validate_role(cls, v):
        allowed = ["admin", "doctor", "patient", "receptionist", "pharmacist"]
        if v not in allowed:
            raise ValueError(f"Role must be one of {allowed}")
        return v


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


class PatientBase(BaseModel):
    name: str
    age: int = Field(gt=0, lt=150)
    gender: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    bloodGroup: Optional[str] = None
    emergencyContact: Optional[str] = None

    @validator("name")
    def name_required(cls, v):
        if not v or not v.strip():
            raise ValueError("Name is required")
        return v.strip()

    @validator("gender")
    def gender_required(cls, v):
        allowed = ["Male", "Female", "Other"]
        if v not in allowed:
            raise ValueError(f"Gender must be one of {allowed}")
        return v


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = Field(None, gt=0, lt=150)
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    bloodGroup: Optional[str] = None
    emergencyContact: Optional[str] = None


class DoctorBase(BaseModel):
    name: str
    specialization: str
    phone: str
    email: str
    department: str
    availability: str = "Mon-Fri 9AM-5PM"

    @validator("name")
    def name_required(cls, v):
        if not v or not v.strip():
            raise ValueError("Name is required")
        return v.strip()

    @validator("email")
    def validate_email(cls, v):
        if "@" not in v:
            raise ValueError("Invalid email")
        return v


class DoctorCreate(DoctorBase):
    pass


class DoctorUpdate(BaseModel):
    name: Optional[str] = None
    specialization: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    availability: Optional[str] = None


class AppointmentBase(BaseModel):
    patientId: str
    doctorId: str
    date: str
    time: str
    reason: Optional[str] = None
    status: str = "Scheduled"

    @validator("status")
    def validate_status(cls, v):
        allowed = ["Scheduled", "Confirmed", "Completed", "Cancelled"]
        if v not in allowed:
            raise ValueError(f"Status must be one of {allowed}")
        return v


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    patientId: Optional[str] = None
    doctorId: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    reason: Optional[str] = None
    status: Optional[str] = None


# --- Auth Routes ---

@app.post("/api/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    users = load_json("users.json")
    user = next((u for u in users if u["email"] == form_data.username), None)
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user["email"]})
    log_audit(user["id"], "LOGIN")
    return {"access_token": access_token, "token_type": "bearer", "user": user}


@app.post("/api/register", response_model=dict)
def register(user_data: UserRegister):
    users = load_json("users.json")
    if any(u["email"] == user_data.email for u in users):
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = {
        "id": f"USR{str(uuid.uuid4())[:8].upper()}",
        "name": user_data.name,
        "email": user_data.email,
        "password": get_password_hash(user_data.password),
        "role": user_data.role,
        "createdAt": datetime.utcnow().isoformat()
    }
    users.append(new_user)
    save_json("users.json", users)
    log_audit(new_user["id"], "REGISTER")
    return {"message": "User registered successfully", "user": {k: v for k, v in new_user.items() if k != "password"}}


@app.get("/api/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return {k: v for k, v in current_user.items() if k != "password"}


@app.post("/api/logout")
def logout(current_user: dict = Depends(get_current_user)):
    log_audit(current_user["id"], "LOGOUT")
    return {"message": "Logged out successfully"}


# --- Patient Routes ---

@app.get("/api/patients")
def get_patients(search: str = "", current_user: dict = Depends(get_current_user)):
    patients = load_json("patients.json")
    if search:
        s = search.lower()
        patients = [p for p in patients if s in (p.get("name") or "").lower() or s in (p.get("patientId") or "").lower() or s in (p.get("phone") or "").lower() or s in (p.get("email") or "").lower()]
    return patients


@app.get("/api/patients/{patient_id}")
def get_patient(patient_id: str, current_user: dict = Depends(get_current_user)):
    patients = load_json("patients.json")
    patient = next((p for p in patients if p["id"] == patient_id or p.get("patientId") == patient_id), None)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@app.post("/api/patients", response_model=dict)
def create_patient(patient_data: PatientCreate, current_user: dict = Depends(get_current_user)):
    patients = load_json("patients.json")
    new_patient = {
        "id": str(uuid.uuid4()),
        "patientId": f"PAT{str(uuid.uuid4())[:8].upper()}",
        "name": patient_data.name,
        "age": patient_data.age,
        "gender": patient_data.gender,
        "phone": patient_data.phone,
        "email": patient_data.email,
        "address": patient_data.address,
        "bloodGroup": patient_data.bloodGroup,
        "emergencyContact": patient_data.emergencyContact,
        "createdAt": datetime.utcnow().isoformat(),
        "updatedAt": datetime.utcnow().isoformat()
    }
    patients.append(new_patient)
    save_json("patients.json", patients)
    log_audit(current_user["id"], "PATIENT_CREATED")
    return {"message": "Patient created successfully", "patient": new_patient}


@app.put("/api/patients/{patient_id}")
def update_patient(patient_id: str, patient_data: PatientUpdate, current_user: dict = Depends(get_current_user)):
    patients = load_json("patients.json")
    patient = next((p for p in patients if p["id"] == patient_id), None)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    update_data = patient_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        patient[key] = value
    patient["updatedAt"] = datetime.utcnow().isoformat()
    save_json("patients.json", patients)
    log_audit(current_user["id"], "PATIENT_UPDATED")
    return {"message": "Patient updated successfully", "patient": patient}


@app.delete("/api/patients/{patient_id}")
def delete_patient(patient_id: str, current_user: dict = Depends(require_roles("admin", "receptionist"))):
    patients = load_json("patients.json")
    patient = next((p for p in patients if p["id"] == patient_id), None)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    patients = [p for p in patients if p["id"] != patient_id]
    save_json("patients.json", patients)
    log_audit(current_user["id"], "PATIENT_DELETED")
    return {"message": "Patient deleted successfully"}


# --- Doctor Routes ---

@app.get("/api/doctors")
def get_doctors(search: str = "", current_user: dict = Depends(get_current_user)):
    doctors = load_json("doctors.json")
    if search:
        s = search.lower()
        doctors = [d for d in doctors if s in d.get("name", "").lower() or s in d.get("specialization", "").lower() or s in d.get("department", "").lower() or s in d.get("doctorId", "").lower()]
    return doctors


@app.get("/api/doctors/{doctor_id}")
def get_doctor(doctor_id: str, current_user: dict = Depends(get_current_user)):
    doctors = load_json("doctors.json")
    doctor = next((d for d in doctors if d["id"] == doctor_id or d.get("doctorId") == doctor_id), None)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


@app.post("/api/doctors", response_model=dict)
def create_doctor(doctor_data: DoctorCreate, current_user: dict = Depends(require_roles("admin"))):
    doctors = load_json("doctors.json")
    new_doctor = {
        "id": str(uuid.uuid4()),
        "doctorId": f"DOC{str(uuid.uuid4())[:8].upper()}",
        "name": doctor_data.name,
        "specialization": doctor_data.specialization,
        "phone": doctor_data.phone,
        "email": doctor_data.email,
        "department": doctor_data.department,
        "availability": doctor_data.availability,
        "createdAt": datetime.utcnow().isoformat(),
        "updatedAt": datetime.utcnow().isoformat()
    }
    doctors.append(new_doctor)
    save_json("doctors.json", doctors)
    log_audit(current_user["id"], "DOCTOR_CREATED")
    return {"message": "Doctor created successfully", "doctor": new_doctor}


@app.put("/api/doctors/{doctor_id}")
def update_doctor(doctor_id: str, doctor_data: DoctorUpdate, current_user: dict = Depends(require_roles("admin"))):
    doctors = load_json("doctors.json")
    doctor = next((d for d in doctors if d["id"] == doctor_id), None)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    update_data = doctor_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        doctor[key] = value
    doctor["updatedAt"] = datetime.utcnow().isoformat()
    save_json("doctors.json", doctors)
    log_audit(current_user["id"], "DOCTOR_UPDATED")
    return {"message": "Doctor updated successfully", "doctor": doctor}


@app.delete("/api/doctors/{doctor_id}")
def delete_doctor(doctor_id: str, current_user: dict = Depends(require_roles("admin"))):
    doctors = load_json("doctors.json")
    doctor = next((d for d in doctors if d["id"] == doctor_id), None)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    doctors = [d for d in doctors if d["id"] != doctor_id]
    save_json("doctors.json", doctors)
    log_audit(current_user["id"], "DOCTOR_DELETED")
    return {"message": "Doctor deleted successfully"}


# --- Appointment Routes ---

@app.get("/api/appointments")
def get_appointments(current_user: dict = Depends(get_current_user)):
    appointments = load_json("appointments.json")
    patients = {p["id"]: p for p in load_json("patients.json")}
    doctors = {d["id"]: d for d in load_json("doctors.json")}
    result = []
    for apt in appointments:
        apt_copy = dict(apt)
        apt_copy["patientName"] = patients.get(apt.get("patientId"), {}).get("name", "Unknown")
        apt_copy["doctorName"] = doctors.get(apt.get("doctorId"), {}).get("name", "Unknown")
        result.append(apt_copy)
    return result


@app.get("/api/appointments/{appointment_id}")
def get_appointment(appointment_id: str, current_user: dict = Depends(get_current_user)):
    appointments = load_json("appointments.json")
    appointment = next((a for a in appointments if a["id"] == appointment_id or a.get("appointmentId") == appointment_id), None)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment


@app.post("/api/appointments", response_model=dict)
def create_appointment(apt_data: AppointmentCreate, current_user: dict = Depends(get_current_user)):
    appointments = load_json("appointments.json")
    doctors = load_json("doctors.json")
    patients = load_json("patients.json")
    doctor = next((d for d in doctors if d["id"] == apt_data.doctorId), None)
    patient = next((p for p in patients if p["id"] == apt_data.patientId), None)
    if not doctor:
        raise HTTPException(status_code=400, detail="Doctor not found")
    if not patient:
        raise HTTPException(status_code=400, detail="Patient not found")
    conflicts = [a for a in appointments if a["doctorId"] == apt_data.doctorId and a["date"] == apt_data.date and a["time"] == apt_data.time and a["status"] != "Cancelled"]
    if conflicts:
        raise HTTPException(status_code=400, detail="Doctor already has an appointment at this time")
    new_apt = {
        "id": str(uuid.uuid4()),
        "appointmentId": f"APT{str(uuid.uuid4())[:8].upper()}",
        "patientId": apt_data.patientId,
        "doctorId": apt_data.doctorId,
        "date": apt_data.date,
        "time": apt_data.time,
        "reason": apt_data.reason,
        "status": apt_data.status,
        "createdAt": datetime.utcnow().isoformat(),
        "updatedAt": datetime.utcnow().isoformat()
    }
    appointments.append(new_apt)
    save_json("appointments.json", appointments)
    log_audit(current_user["id"], "APPOINTMENT_CREATED")
    return {"message": "Appointment created successfully", "appointment": new_apt}


@app.put("/api/appointments/{appointment_id}")
def update_appointment(appointment_id: str, apt_data: AppointmentUpdate, current_user: dict = Depends(get_current_user)):
    appointments = load_json("appointments.json")
    appointment = next((a for a in appointments if a["id"] == appointment_id), None)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    update_data = apt_data.dict(exclude_unset=True)
    if "doctorId" in update_data or "date" in update_data or "time" in update_data:
        doctor_id = update_data.get("doctorId", appointment["doctorId"])
        date = update_data.get("date", appointment["date"])
        time = update_data.get("time", appointment["time"])
        conflicts = [a for a in appointments if a["id"] != appointment_id and a["doctorId"] == doctor_id and a["date"] == date and a["time"] == time and a["status"] != "Cancelled"]
        if conflicts:
            raise HTTPException(status_code=400, detail="Doctor already has an appointment at this time")
    for key, value in update_data.items():
        appointment[key] = value
    appointment["updatedAt"] = datetime.utcnow().isoformat()
    save_json("appointments.json", appointments)
    log_audit(current_user["id"], "APPOINTMENT_UPDATED")
    return {"message": "Appointment updated successfully", "appointment": appointment}


@app.delete("/api/appointments/{appointment_id}")
def delete_appointment(appointment_id: str, current_user: dict = Depends(get_current_user)):
    appointments = load_json("appointments.json")
    appointment = next((a for a in appointments if a["id"] == appointment_id), None)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    appointments = [a for a in appointments if a["id"] != appointment_id]
    save_json("appointments.json", appointments)
    log_audit(current_user["id"], "APPOINTMENT_CANCELLED")
    return {"message": "Appointment cancelled successfully"}


# --- Stats ---

@app.get("/api/stats")
def get_stats(current_user: dict = Depends(get_current_user)):
    patients = load_json("patients.json")
    doctors = load_json("doctors.json")
    appointments = load_json("appointments.json")
    today = datetime.utcnow().strftime("%Y-%m-%d")
    today_appointments = [a for a in appointments if a.get("date") == today]
    return {
        "totalPatients": len(patients),
        "totalDoctors": len(doctors),
        "todayAppointments": len(today_appointments),
        "totalAppointments": len(appointments)
    }


@app.get("/api/audit-logs")
def get_audit_logs(current_user: dict = Depends(require_roles("admin"))):
    logs = load_json("auditLogs.json")
    users = {u["id"]: u for u in load_json("users.json")}
    result = []
    for log in logs:
        log_copy = dict(log)
        log_copy["userName"] = users.get(log.get("userId"), {}).get("name", "Unknown")
        result.append(log_copy)
    return sorted(result, key=lambda x: x.get("timestamp", ""), reverse=True)
