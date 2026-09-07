import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import Modal from '../components/Modal';
import { useToast } from '../components/Toast';
import { Plus, Search, Edit, Trash2 } from 'lucide-react';

export default function Doctors() {
  const [doctors, setDoctors] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingDoctor, setEditingDoctor] = useState(null);
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const { toasts, addToast, removeToast } = useToast();
  const [formData, setFormData] = useState({
    name: '', specialization: '', phone: '', email: '', department: '', availability: 'Mon-Fri 9AM-5PM'
  });

  const loadDoctors = async () => {
    setLoading(true);
    try {
      const data = await api.getDoctors(search);
      setDoctors(data);
    } catch (e) {
      addToast(e.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(loadDoctors, 300);
    return () => clearTimeout(timer);
  }, [search]);

  const openCreate = () => {
    setEditingDoctor(null);
    setFormData({ name: '', specialization: '', phone: '', email: '', department: '', availability: 'Mon-Fri 9AM-5PM' });
    setModalOpen(true);
  };

  const openEdit = (doctor) => {
    setEditingDoctor(doctor);
    setFormData({
      name: doctor.name,
      specialization: doctor.specialization,
      phone: doctor.phone,
      email: doctor.email,
      department: doctor.department,
      availability: doctor.availability
    });
    setModalOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingDoctor) {
        await api.updateDoctor(editingDoctor.id, formData);
        addToast('Doctor updated successfully');
      } else {
        await api.createDoctor(formData);
        addToast('Doctor created successfully');
      }
      setModalOpen(false);
      loadDoctors();
    } catch (e) {
      addToast(e.message, 'error');
    }
  };

  const handleDelete = async () => {
    try {
      await api.deleteDoctor(deleteConfirm.id);
      addToast('Doctor deleted successfully');
      setDeleteConfirm(null);
      loadDoctors();
    } catch (e) {
      addToast(e.message, 'error');
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Doctors</h1>
        <button className="btn btn-primary" onClick={openCreate}>
          <Plus size={18} />
          Add Doctor
        </button>
      </div>

      <div className="search-bar">
        <div style={{ position: 'relative', flex: 1, maxWidth: 400 }}>
          <Search size={18} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: '#9ca3af' }} />
          <input
            type="text"
            className="search-input"
            placeholder="Search by name, specialization, department..."
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
      ) : doctors.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">🩺</div>
          <div className="empty-state-title">No doctors found</div>
          <p>Add your first doctor to get started.</p>
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Doctor ID</th>
                <th>Name</th>
                <th>Specialization</th>
                <th>Department</th>
                <th>Phone</th>
                <th>Email</th>
                <th>Availability</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {doctors.map(doctor => (
                <tr key={doctor.id}>
                  <td>{doctor.doctorId}</td>
                  <td>{doctor.name}</td>
                  <td>{doctor.specialization}</td>
                  <td>{doctor.department}</td>
                  <td>{doctor.phone}</td>
                  <td>{doctor.email}</td>
                  <td>{doctor.availability}</td>
                  <td>
                    <div style={{ display: 'flex', gap: 8 }}>
                      <button className="btn btn-sm btn-secondary" onClick={() => openEdit(doctor)}>
                        <Edit size={14} />
                      </button>
                      <button className="btn btn-sm btn-danger" onClick={() => setDeleteConfirm(doctor)}>
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
        title={editingDoctor ? 'Edit Doctor' : 'Add New Doctor'}
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setModalOpen(false)}>Cancel</button>
            <button className="btn btn-primary" onClick={handleSubmit}>
              {editingDoctor ? 'Update' : 'Create'}
            </button>
          </>
        }
      >
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Name *</label>
            <input className="form-input" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} required />
          </div>
          <div className="form-group">
            <label className="form-label">Specialization *</label>
            <input className="form-input" value={formData.specialization} onChange={e => setFormData({...formData, specialization: e.target.value})} required />
          </div>
          <div className="form-group">
            <label className="form-label">Department *</label>
            <input className="form-input" value={formData.department} onChange={e => setFormData({...formData, department: e.target.value})} required />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div className="form-group">
              <label className="form-label">Phone *</label>
              <input className="form-input" value={formData.phone} onChange={e => setFormData({...formData, phone: e.target.value})} required />
            </div>
            <div className="form-group">
              <label className="form-label">Email *</label>
              <input type="email" className="form-input" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} required />
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Availability</label>
            <input className="form-input" value={formData.availability} onChange={e => setFormData({...formData, availability: e.target.value})} />
          </div>
        </form>
      </Modal>

      <Modal
        isOpen={!!deleteConfirm}
        onClose={() => setDeleteConfirm(null)}
        title="Confirm Delete"
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setDeleteConfirm(null)}>Cancel</button>
            <button className="btn btn-danger" onClick={handleDelete}>Delete</button>
          </>
        }
      >
        <p>Are you sure you want to delete doctor <strong>{deleteConfirm?.name}</strong>?</p>
      </Modal>

      <Toast toasts={toasts} removeToast={removeToast} />
    </div>
  );
}
