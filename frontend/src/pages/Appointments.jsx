import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import Modal from '../components/Modal';
import { useToast } from '../components/Toast';
import { Plus, Search, Edit, Trash2, X } from 'lucide-react';

export default function Appointments() {
  const [appointments, setAppointments] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [patients, setPatients] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingApt, setEditingApt] = useState(null);
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const { toasts, addToast, removeToast } = useToast();
  const [formData, setFormData] = useState({
    patientId: '', doctorId: '', date: '', time: '', reason: '', status: 'Scheduled'
  });

  const loadAll = async () => {
    setLoading(true);
    try {
      const [aptData, docData, patData] = await Promise.all([
        api.getAppointments(),
        api.getDoctors(),
        api.getPatients()
      ]);
      setAppointments(aptData);
      setDoctors(docData);
      setPatients(patData);
    } catch (e) {
      addToast(e.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAll();
  }, []);

  const openCreate = () => {
    setEditingApt(null);
    setFormData({ patientId: '', doctorId: '', date: '', time: '', reason: '', status: 'Scheduled' });
    setModalOpen(true);
  };

  const openEdit = (apt) => {
    setEditingApt(apt);
    setFormData({
      patientId: apt.patientId,
      doctorId: apt.doctorId,
      date: apt.date,
      time: apt.time,
      reason: apt.reason || '',
      status: apt.status
    });
    setModalOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingApt) {
        await api.updateAppointment(editingApt.id, formData);
        addToast('Appointment updated successfully');
      } else {
        await api.createAppointment(formData);
        addToast('Appointment created successfully');
      }
      setModalOpen(false);
      loadAll();
    } catch (e) {
      addToast(e.message, 'error');
    }
  };

  const handleDelete = async () => {
    try {
      await api.deleteAppointment(deleteConfirm.id);
      addToast('Appointment cancelled successfully');
      setDeleteConfirm(null);
      loadAll();
    } catch (e) {
      addToast(e.message, 'error');
    }
  };

  const getStatusClass = (status) => {
    return `badge badge-${status.toLowerCase()}`;
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Appointments</h1>
        <button className="btn btn-primary" onClick={openCreate}>
          <Plus size={18} />
          Book Appointment
        </button>
      </div>

      <div className="search-bar">
        <div style={{ position: 'relative', flex: 1, maxWidth: 400 }}>
          <Search size={18} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: '#9ca3af' }} />
          <input
            type="text"
            className="search-input"
            placeholder="Search appointments..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ paddingLeft: 40 }}
          />
        </div>
      </div>

      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: 40 }}>
          <div className="loading-spinner"></div>
        </div>
      ) : appointments.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📅</div>
          <div className="empty-state-title">No appointments found</div>
          <p>Book your first appointment to get started.</p>
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Appointment ID</th>
                <th>Patient</th>
                <th>Doctor</th>
                <th>Date</th>
                <th>Time</th>
                <th>Reason</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {appointments.filter(apt => {
                if (!search) return true;
                const s = search.toLowerCase();
                return apt.patientName.toLowerCase().includes(s) || apt.doctorName.toLowerCase().includes(s) || apt.date.includes(s) || apt.status.toLowerCase().includes(s);
              }).map(apt => (
                <tr key={apt.id}>
                  <td>{apt.appointmentId}</td>
                  <td>{apt.patientName}</td>
                  <td>{apt.doctorName}</td>
                  <td>{apt.date}</td>
                  <td>{apt.time}</td>
                  <td>{apt.reason || '-'}</td>
                  <td>
                    <span className={getStatusClass(apt.status)}>
                      {apt.status}
                    </span>
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: 8 }}>
                      <button className="btn btn-sm btn-secondary" onClick={() => openEdit(apt)}>
                        <Edit size={14} />
                      </button>
                      <button className="btn btn-sm btn-danger" onClick={() => setDeleteConfirm(apt)}>
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editingApt ? 'Edit Appointment' : 'Book Appointment'}
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setModalOpen(false)}>Cancel</button>
            <button className="btn btn-primary" onClick={handleSubmit}>
              {editingApt ? 'Update' : 'Book'}
            </button>
          </>
        }
      >
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Patient *</label>
            <select className="form-input" value={formData.patientId} onChange={e => setFormData({...formData, patientId: e.target.value})} required>
              <option value="">Select Patient</option>
              {patients.map(p => (
                <option key={p.id} value={p.id}>{p.name} ({p.patientId})</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Doctor *</label>
            <select className="form-input" value={formData.doctorId} onChange={e => setFormData({...formData, doctorId: e.target.value})} required>
              <option value="">Select Doctor</option>
              {doctors.map(d => (
                <option key={d.id} value={d.id}>{d.name} - {d.specialization}</option>
              ))}
            </select>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div className="form-group">
              <label className="form-label">Date *</label>
              <input type="date" className="form-input" value={formData.date} onChange={e => setFormData({...formData, date: e.target.value})} required />
            </div>
            <div className="form-group">
              <label className="form-label">Time *</label>
              <input type="time" className="form-input" value={formData.time} onChange={e => setFormData({...formData, time: e.target.value})} required />
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Reason</label>
            <input className="form-input" value={formData.reason} onChange={e => setFormData({...formData, reason: e.target.value})} />
          </div>
          <div className="form-group">
            <label className="form-label">Status</label>
            <select className="form-input" value={formData.status} onChange={e => setFormData({...formData, status: e.target.value})}>
              <option value="Scheduled">Scheduled</option>
              <option value="Confirmed">Confirmed</option>
              <option value="Completed">Completed</option>
              <option value="Cancelled">Cancelled</option>
            </select>
          </div>
        </form>
      </Modal>

      <Modal
        isOpen={!!deleteConfirm}
        onClose={() => setDeleteConfirm(null)}
        title="Confirm Cancel"
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setDeleteConfirm(null)}>Cancel</button>
            <button className="btn btn-danger" onClick={handleDelete}>Cancel Appointment</button>
          </>
        }
      >
        <p>Are you sure you want to cancel the appointment for <strong>{deleteConfirm?.patientName}</strong> with <strong>{deleteConfirm?.doctorName}</strong>?</p>
      </Modal>

      <Toast toasts={toasts} removeToast={removeToast} />
    </div>
  );
}
