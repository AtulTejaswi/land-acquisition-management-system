import React, { useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../../store/AuthContext';
import { Sidebar } from './Sidebar';
import { Button } from '../ui/button';

const DEMO_ROLES = [
  { value: 'super_admin', label: '🔑 Super Admin', route: '/admin/dashboard' },
  { value: 'state_authority', label: '🏛️ State Authority', route: '/state/dashboard' },
  { value: 'district_officer', label: '📋 District Officer', route: '/district/dashboard' },
  { value: 'agency', label: '🏗️ Agency', route: '/agency/projects' },
  { value: 'field_officer', label: '📱 Field Officer', route: '/field/home' },
  { value: 'citizen', label: '👤 Citizen', route: '/citizen/track' },
];

const ROLE_LABELS: Record<string, string> = {
  super_admin: '🔑 Super Admin — Central Ministry',
  state_authority: '🏛️ State Authority',
  district_officer: '📋 District Collector / LAO',
  agency: '🏗️ Project Implementing Agency',
  field_officer: '📱 Field Officer',
  citizen: '👤 Citizen / Land Owner',
};

const FIELD_TABS = [
  { icon: '🏠', label: 'Home', path: '/field/home' },
  { icon: '📋', label: 'Surveys', path: '/field/surveys' },
  { icon: '📸', label: 'Camera', path: '/field/camera' },
  { icon: '👤', label: 'Profile', path: '/field/profile' },
];

export function RoleShell() {
  const { user, logout, switchRole } = useAuth();
  const navigate = useNavigate();
  const [showDemoSwitcher, setShowDemoSwitcher] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleRoleSwitch = (role: string, route: string) => {
    if (switchRole) switchRole(role);
    navigate(route);
    setShowDemoSwitcher(false);
  };

  if (!user) return null;

  const isField = user.role_name === 'field_officer';

  return (
    <div className="flex h-screen overflow-hidden">
      {!isField && <Sidebar role={user.role_name} />}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Topbar */}
        <header className="h-14 border-b border-slate-200 bg-white/80 backdrop-blur-md flex items-center justify-between px-6">
          <div className="flex items-center gap-3">
            <span className="text-sm text-slate-500">{ROLE_LABELS[user.role_name] || user.role_name}</span>
          </div>
          <div className="flex items-center gap-3">
            {/* Demo Mode Role Switcher */}
            <div className="relative">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowDemoSwitcher(!showDemoSwitcher)}
                className="text-xs"
              >
                🔄 Switch Role (Demo)
              </Button>
              {showDemoSwitcher && (
                <div className="absolute right-0 top-full mt-2 bg-white border border-slate-200 rounded-xl shadow-xl p-2 z-50 min-w-[200px]">
                  <div className="text-[10px] text-slate-400 px-2 py-1 font-semibold uppercase tracking-wide">Dev-Only Demo Switcher</div>
                  {DEMO_ROLES.map((r) => (
                    <button
                      key={r.value}
                      onClick={() => handleRoleSwitch(r.value, r.route)}
                      className={`w-full text-left px-3 py-2 text-sm rounded-lg transition-colors ${
                        user.role_name === r.value
                          ? 'bg-primary-50 text-primary-600 font-medium'
                          : 'text-slate-700 hover:bg-slate-50'
                      }`}
                    >
                      {r.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
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

      {/* Mobile Bottom Tab Bar (Field Officer only) */}
      {isField && (
        <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-slate-200 flex items-center justify-around py-2 px-4 z-50">
          {FIELD_TABS.map((tab) => {
            const isActive = window.location.pathname === tab.path;
            return (
              <button
                key={tab.path}
                onClick={() => navigate(tab.path)}
                className={`flex flex-col items-center gap-0.5 min-w-[44px] min-h-[44px] justify-center rounded-lg transition-colors ${
                  isActive ? 'text-primary-600 bg-primary-50' : 'text-slate-400'
                }`}
              >
                <span className="text-xl">{tab.icon}</span>
                <span className="text-[10px] font-medium">{tab.label}</span>
              </button>
            );
          })}
        </nav>
      )}
    </div>
  );
}
