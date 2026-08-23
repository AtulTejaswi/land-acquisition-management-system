import React from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../../store/AuthContext';
import { Sidebar } from './Sidebar';
import { Button } from '../ui/button';

export function RoleShell() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!user) return null;

  const roleLabels: Record<string, string> = {
    super_admin: '🔑 Super Admin — Central Ministry',
    state_authority: '🏛️ State Authority',
    district_officer: '📋 District Collector / LAO',
    agency: '🏗️ Project Implementing Agency',
    field_officer: '📱 Field Officer',
    citizen: '👤 Citizen / Land Owner',
  };

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar role={user.role_name} />
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Topbar */}
        <header className="h-14 border-b border-slate-200 bg-white/80 backdrop-blur-md flex items-center justify-between px-6">
          <div className="flex items-center gap-3">
            <span className="text-sm text-slate-500">{roleLabels[user.role_name] || user.role_name}</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="text-right">
              <div className="text-sm font-medium text-slate-900">{user.full_name}</div>
              <div className="text-xs text-slate-400">{user.email}</div>
            </div>
            <Button variant="ghost" size="sm" onClick={handleLogout} className="text-slate-500">
              Logout
            </Button>
          </div>
        </header>

        {/* Main content */}
        <main className="flex-1 overflow-y-auto bg-slate-50 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
