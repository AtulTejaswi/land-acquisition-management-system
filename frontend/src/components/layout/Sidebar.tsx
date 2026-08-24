import React from 'react';
import { NavLink } from 'react-router-dom';
import { cn } from '@/lib/utils';

interface NavItem {
  label: string;
  path: string;
  icon: string;
}

const roleNavItems: Record<string, NavItem[]> = {
  super_admin: [
    { label: 'National Dashboard', path: '/admin/dashboard', icon: '📊' },
    { label: 'Projects', path: '/admin/projects', icon: '📁' },
    { label: 'User Management', path: '/admin/users', icon: '👥' },
    { label: 'Reports / MIS', path: '/admin/reports', icon: '📈' },
    { label: 'GIS Map', path: '/admin/gis', icon: '🗺️' },
    { label: 'Notifications', path: '/admin/notifications', icon: '🔔' },
    { label: 'Settings', path: '/admin/settings', icon: '⚙️' },
  ],
  state_authority: [
    { label: 'State Dashboard', path: '/state/dashboard', icon: '📊' },
    { label: 'Projects', path: '/state/projects', icon: '📁' },
    { label: 'Districts', path: '/state/districts', icon: '🏘️' },
    { label: 'GIS Map', path: '/state/gis', icon: '🗺️' },
    { label: 'Compensation', path: '/state/compensation', icon: '💰' },
    { label: 'Reports', path: '/state/reports', icon: '📈' },
  ],
  district_officer: [
    { label: 'District Dashboard', path: '/district/dashboard', icon: '📊' },
    { label: 'Verification Queue', path: '/district/verification', icon: '✅' },
    { label: 'Parcels', path: '/district/parcels', icon: '🗺️' },
    { label: 'Compensation Desk', path: '/district/compensation', icon: '💰' },
    { label: 'R&R Management', path: '/district/rr', icon: '🏘️' },
    { label: 'Notifications', path: '/district/notifications', icon: '🔔' },
  ],
  agency: [
    { label: 'My Projects', path: '/agency/projects', icon: '📁' },
    { label: 'Create Proposal', path: '/agency/create', icon: '➕' },
    { label: 'GIS Map', path: '/agency/gis', icon: '🗺️' },
    { label: 'Documents', path: '/agency/documents', icon: '📄' },
  ],
  field_officer: [
    { label: 'Home', path: '/field/home', icon: '🏠' },
    { label: 'My Surveys', path: '/field/surveys', icon: '📋' },
    { label: 'Camera', path: '/field/camera', icon: '📸' },
    { label: 'Profile', path: '/field/profile', icon: '👤' },
  ],
  citizen: [
    { label: 'Track Status', path: '/citizen/track', icon: '🔍' },
    { label: 'My Compensation', path: '/citizen/compensation', icon: '💰' },
    { label: 'My R&R', path: '/citizen/rr', icon: '🏘️' },
    { label: 'My Documents', path: '/citizen/documents', icon: '📄' },
    { label: 'Notifications', path: '/citizen/notifications', icon: '🔔' },
  ],
};

interface SidebarProps {
  role: string;
}

export function Sidebar({ role }: SidebarProps) {
  const items = roleNavItems[role] || roleNavItems.super_admin;
  const isField = role === 'field_officer';

  return (
    <aside
      className={cn(
        'h-screen bg-white border-r border-slate-200 flex flex-col',
        isField ? 'w-16' : 'w-64',
      )}
    >
      {/* Logo */}
      <div className={cn('p-4 border-b border-slate-200', isField ? 'px-2' : '')}>
        {isField ? (
          <div className="text-lg font-bold text-primary-500">N</div>
        ) : (
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-primary-500 flex items-center justify-center text-white font-bold text-sm">N</div>
            <div>
              <div className="font-bold text-slate-900 text-sm">NLAMS</div>
              <div className="text-[10px] text-slate-400">Land Acquisition System</div>
            </div>
          </div>
        )}
      </div>

      {/* Nav Items */}
      <nav className="flex-1 p-2 space-y-1 overflow-y-auto">
        {items.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                isField && 'justify-center px-2',
                isActive
                  ? 'bg-primary-50 text-primary-600'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900',
              )
            }
            title={isField ? item.label : undefined}
          >
            <span className="text-lg">{item.icon}</span>
            {!isField && <span>{item.label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      {!isField && (
        <div className="p-4 border-t border-slate-200">
          <div className="text-xs text-slate-400 text-center">
            NLAMS v1.0 • Sandbox/Demo Mode
          </div>
        </div>
      )}
    </aside>
  );
}
