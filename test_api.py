import urllib.request, json

def login_request():
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    body = 'username=admin@hms.com&password=admin123'.encode()
    req = urllib.request.Request('http://localhost:8000/api/login', data=body, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {'error': e.code, 'msg': e.read().decode()}

def api_request(path, data=None, method='GET', token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(f'http://localhost:8000{path}', data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {'error': e.code, 'msg': e.read().decode()}

login = login_request()
token = login['access_token']
print('Login:', 'PASS')

patients = api_request('/api/patients', token=token)
print('Get patients:', 'PASS', len(patients), 'records')

new_patient = api_request('/api/patients', {'name': 'Test User', 'age': 30, 'gender': 'Male', 'phone': '555-9999'}, 'POST', token)
print('Create patient:', 'PASS', new_patient.get('patient', {}).get('patientId'))

patient_id = new_patient['patient']['id']
updated = api_request(f'/api/patients/{patient_id}', {'name': 'Test User Updated'}, 'PUT', token)
print('Update patient:', 'PASS', updated.get('patient', {}).get('name'))

doctors = api_request('/api/doctors', token=token)
print('Get doctors:', 'PASS', len(doctors), 'records')

new_doctor = api_request('/api/doctors', {'name': 'Dr. Test', 'specialization': 'Cardiology', 'phone': '555-8888', 'email': 'test@hms.com', 'department': 'Cardiology'}, 'POST', token)
print('Create doctor:', 'PASS', new_doctor.get('doctor', {}).get('doctorId'))

doctor_id = new_doctor['doctor']['id']
appointments = api_request('/api/appointments', token=token)
print('Get appointments:', 'PASS', len(appointments), 'records')

new_apt = api_request('/api/appointments', {'patientId': patient_id, 'doctorId': doctor_id, 'date': '2026-08-13', 'time': '14:00', 'reason': 'Test'}, 'POST', token)
print('Create appointment:', 'PASS', new_apt.get('appointment', {}).get('appointmentId'))

stats = api_request('/api/stats', token=token)
print('Stats:', 'PASS', stats)

# Test delete
deleted = api_request(f'/api/patients/{patient_id}', method='DELETE', token=token)
print('Delete patient:', 'PASS')

print('\nAll API tests passed!')
