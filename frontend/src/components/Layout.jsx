import React, { useState } from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Menu, X } from 'lucide-react';

export default function Layout() {
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const getInitials = (name) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  const navItems = [
    { to: '/dashboard', label: 'Dashboard', icon: '🏠', exact: true },
    { to: '/dashboard/patients', label: 'Patients', icon: '👥', roles: ['admin', 'receptionist', 'doctor', 'patient'] },
    { to: '/dashboard/doctors', label: 'Doctors', icon: '🩺', roles: ['admin', 'receptionist'] },
    { to: '/dashboard/appointments', label: 'Appointments', icon: '📅', roles: ['admin', 'receptionist', 'doctor', 'patient'] },
  ];

  const visibleNavItems = navItems.filter(item => !item.roles || item.roles.includes(user?.role));

  return (
    <div className="app-layout">
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <div className="sidebar-brand">
            <div className="sidebar-logo">H</div>
            <div>
              <div className="sidebar-title">HMS</div>
              <div className="sidebar-subtitle">Hospital Management</div>
            </div>
          </div>
        </div>
        <nav className="sidebar-nav">
          <div className="nav-section">
            <div className="nav-section-title">Main Menu</div>
            {visibleNavItems.map(item => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.exact}
                className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                onClick={() => setSidebarOpen(false)}
              >
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </NavLink>
            ))}
          </div>
        </nav>
        <div className="sidebar-footer">
          <div className="sidebar-user">
            <div className="sidebar-avatar">{getInitials(user?.name || 'U')}</div>
            <div className="sidebar-user-info">
              <div className="sidebar-user-name">{user?.name}</div>
              <div className="sidebar-user-role">{user?.role}</div>
            </div>
          </div>
          <button className="sidebar-logout" onClick={logout}>
            Logout
          </button>
        </div>
      </aside>
      <main className="main-content">
        <header className="topbar">
          <button className="mobile-toggle" onClick={() => setSidebarOpen(!sidebarOpen)}>
            {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
          <h1 className="topbar-title">Hospital Management System</h1>
          <div></div>
        </header>
        <div className="page-content">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
