import React from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';

export default function About() {
  return (
    <div className="min-h-screen bg-slate-50">
      {/* Navbar */}
      <nav className="border-b border-slate-200 bg-white/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-primary-500 flex items-center justify-center text-white font-bold text-sm">N</div>
            <span className="font-bold text-slate-900">NLAMS</span>
          </Link>
          <Link to="/login"><Button size="sm">Sign In</Button></Link>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-6 py-16 space-y-12">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">About NLAMS</h1>
          <p className="text-slate-500 mt-4 text-lg">
            The National Land Acquisition & Management System (NLAMS) is a comprehensive e-Governance platform
            designed to digitize and streamline India's land acquisition lifecycle as per the Right to Fair
            Compensation and Transparency in Land Acquisition, Rehabilitation and Resettlement Act, 2013 (LARR Act).
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardContent className="p-6">
              <h3 className="font-semibold text-slate-900 mb-2">🎯 Mission</h3>
              <p className="text-sm text-slate-600">
                To create a transparent, efficient, and citizen-friendly platform for managing land acquisition
                across India, ensuring fair compensation and timely rehabilitation for affected families.
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <h3 className="font-semibold text-slate-900 mb-2">👁️ Vision</h3>
              <p className="text-sm text-slate-600">
                A fully digital, GIS-powered national system that connects citizens, field officers, district
                authorities, state agencies, and central ministries in a single transparent workflow.
              </p>
            </CardContent>
          </Card>
        </div>

        <div>
          <h2 className="text-xl font-bold text-slate-900 mb-4">14-Stage Lifecycle</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {[
              'Project Proposal', 'DPR Upload', 'Land Requirement', 'State Review',
              'District Verification', 'GIS Mapping', 'Legal Notification',
              'Objection Handling', 'Compensation Assessment', 'Award Declaration',
              'Payment Disbursement', 'Physical Possession', 'Rehabilitation & Resettlement', 'Project Completion',
            ].map((stage, i) => (
              <div key={i} className="flex items-center gap-2 p-3 bg-white border border-slate-200 rounded-lg">
                <span className="text-xs font-bold text-primary-600 w-6">{i + 1}</span>
                <span className="text-sm text-slate-700">{stage}</span>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h2 className="text-xl font-bold text-slate-900 mb-4">6 Stakeholder Roles</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { role: 'Super Admin', desc: 'Central Ministry oversight and national analytics', icon: '🔑' },
              { role: 'State Authority', desc: 'State-level project monitoring', icon: '🏛️' },
              { role: 'District Collector', desc: 'Verification and compensation desk', icon: '📋' },
              { role: 'Project Agency', desc: 'Project proposals and document management', icon: '🏗️' },
              { role: 'Field Officer', desc: 'Mobile-first inspections and surveys', icon: '📱' },
              { role: 'Citizen', desc: 'Transparency portal for tracking status', icon: '👤' },
            ].map((r, i) => (
              <div key={i} className="flex items-start gap-3 p-4 bg-white border border-slate-200 rounded-xl">
                <span className="text-2xl">{r.icon}</span>
                <div>
                  <div className="font-semibold text-sm text-slate-900">{r.role}</div>
                  <div className="text-xs text-slate-500 mt-0.5">{r.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Sandbox notice */}
        <Card className="border-amber-200 bg-amber-50/50">
          <CardContent className="p-4 flex items-center gap-3">
            <span className="text-2xl">⚠️</span>
            <div>
              <div className="text-sm font-semibold text-amber-700">Sandbox/Demo Mode</div>
              <div className="text-xs text-amber-600">This is a demonstration platform built for Smart India Hackathon. SMS, PFMS, DigiLocker, and e-Sign integrations are mocked for demo purposes.</div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
