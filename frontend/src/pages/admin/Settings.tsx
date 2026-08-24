import React from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../../store/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';

export default function SettingsPage() {
  const { user } = useAuth();

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold text-slate-900">⚙️ Settings</h1>
        <p className="text-slate-500 text-sm">Manage your account and system preferences</p>
      </motion.div>

      <Card>
        <CardHeader>
          <CardTitle>Profile Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-medium text-slate-500">Full Name</label>
              <Input value={user?.full_name || ''} readOnly className="bg-slate-50" />
            </div>
            <div>
              <label className="text-xs font-medium text-slate-500">Email</label>
              <Input value={user?.email || ''} readOnly className="bg-slate-50" />
            </div>
            <div>
              <label className="text-xs font-medium text-slate-500">Phone</label>
              <Input value={user?.phone || ''} readOnly className="bg-slate-50" />
            </div>
            <div>
              <label className="text-xs font-medium text-slate-500">Role</label>
              <Input
                value={user?.role_name?.replace(/_/g, ' ') || ''}
                readOnly
                className="bg-slate-50 capitalize"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>System Preferences</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between p-3 border border-slate-200 rounded-lg">
            <div>
              <div className="text-sm font-medium text-slate-900">Email Notifications</div>
              <div className="text-xs text-slate-500">Receive email alerts for important updates</div>
            </div>
            <div className="text-xs bg-emerald-100 text-emerald-700 px-2 py-1 rounded-full">Enabled</div>
          </div>
          <div className="flex items-center justify-between p-3 border border-slate-200 rounded-lg">
            <div>
              <div className="text-sm font-medium text-slate-900">SMS Notifications</div>
              <div className="text-xs text-slate-500">Receive SMS for payment and status updates</div>
            </div>
            <div className="text-xs bg-amber-100 text-amber-700 px-2 py-1 rounded-full">Demo Mode</div>
          </div>
          <div className="flex items-center justify-between p-3 border border-slate-200 rounded-lg">
            <div>
              <div className="text-sm font-medium text-slate-900">Sandbox/Demo Mode</div>
              <div className="text-xs text-slate-500">All external integrations are mocked</div>
            </div>
            <div className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">Active</div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>About NLAMS</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm text-slate-600">
            <p><strong>Version:</strong> 1.0.0</p>
            <p><strong>Built for:</strong> Smart India Hackathon (SIH)</p>
            <p><strong>Tech Stack:</strong> React 18 + FastAPI + PostgreSQL + PostGIS</p>
            <p className="text-xs text-slate-400 pt-2">
              National Land Acquisition & Management System — digitizing India's land acquisition lifecycle.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
