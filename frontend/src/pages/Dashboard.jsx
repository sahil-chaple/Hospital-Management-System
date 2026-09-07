import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../utils/api';
import { Users, UserCheck, Calendar, ClipboardList } from 'lucide-react';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [recentAppointments, setRecentAppointments] = useState([]);
  const [recentPatients, setRecentPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    Promise.all([
      api.getStats(),
      api.getAppointments(),
      api.getPatients()
    ]).then(([statsData, appointments, patients]) => {
      setStats(statsData);
      setRecentAppointments(appointments.slice(0, 5));
      setRecentPatients(patients.slice(0, 5));
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '400px' }}>
        <div className="loading-spinner"></div>
      </div>
    );
  }

  const statCards = [
    { title: 'Total Patients', value: stats?.totalPatients || 0, icon: '👥', color: '#dbeafe' },
    { title: 'Total Doctors', value: stats?.totalDoctors || 0, icon: '🩺', color: '#d1fae5' },
    { title: "Today's Appointments", value: stats?.todayAppointments || 0, icon: '📅', color: '#fef3c7' },
    { title: 'Total Appointments', value: stats?.totalAppointments || 0, icon: '📋', color: '#f3e8ff' },
  ];

  return (
    <div>
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 4 }}>Welcome back, {user?.name}</h1>
        <p style={{ color: '#6b7280', fontSize: 14 }}>Here's what's happening at your hospital today.</p>
      </div>

      <div className="stats-grid">
        {statCards.map((card, idx) => (
          <div key={idx} className="stat-card">
            <div className="stat-card-header">
              <span className="stat-card-title">{card.title}</span>
              <span className="stat-card-icon" style={{ background: card.color }}>{card.icon}</span>
            </div>
            <div className="stat-card-value">{card.value}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: 24 }}>
        <div style={{ background: 'white', borderRadius: 12, padding: 24, boxShadow: '0 1px 3px rgba(0,0,0,0.1)', border: '1px solid #e5e7eb' }}>
          <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>Today's Appointments</h2>
          {recentAppointments.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">📅</div>
              <div className="empty-state-title">No appointments today</div>
            </div>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Patient</th>
                  <th>Doctor</th>
                  <th>Time</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {recentAppointments.map(apt => (
                  <tr key={apt.id}>
                    <td>{apt.patientName}</td>
                    <td>{apt.doctorName}</td>
                    <td>{apt.time}</td>
                    <td>
                      <span className={`badge badge-${apt.status.toLowerCase()}`}>
                        {apt.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div style={{ background: 'white', borderRadius: 12, padding: 24, boxShadow: '0 1px 3px rgba(0,0,0,0.1)', border: '1px solid #e5e7eb' }}>
          <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>Recent Patients</h2>
          {recentPatients.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">👥</div>
              <div className="empty-state-title">No patients yet</div>
            </div>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Gender</th>
                  <th>Phone</th>
                </tr>
              </thead>
              <tbody>
                {recentPatients.map(patient => (
                  <tr key={patient.id}>
                    <td>{patient.patientId}</td>
                    <td>{patient.name}</td>
                    <td>{patient.gender}</td>
                    <td>{patient.phone}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
