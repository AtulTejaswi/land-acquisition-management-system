import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Card, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';

const features = [
  {
    icon: '🗺️',
    title: 'GIS Parcel Mapping',
    description: 'Interactive maps with real GeoJSON polygons, draw tools, and click-to-inspect parcels.',
  },
  {
    icon: '🤖',
    title: 'AI-Powered Insights',
    description: 'Delay prediction, risk scoring, and missing document detection powered by intelligent algorithms.',
  },
  {
    icon: '🇮🇳',
    title: 'Citizen Transparency',
    description: 'End-to-end tracking of land acquisition status, compensation, and payment for citizens.',
  },
  {
    icon: '📊',
    title: 'National Dashboard',
    description: 'Real-time overview of all projects across India with state-wise heatmap visualization.',
  },
  {
    icon: '📱',
    title: 'Mobile Field Officer',
    description: 'GPS-enabled inspections with geo-tagged photo capture and real-time survey submissions.',
  },
  {
    icon: '💰',
    title: 'Full Payment Chain',
    description: 'Compensation assessment, PFMS integration, and rehabilitation & resettlement tracking.',
  },
];

export default function Landing() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      {/* Navbar */}
      <nav className="border-b border-slate-200 bg-white/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-primary-500 flex items-center justify-center text-white font-bold text-sm">N</div>
            <span className="font-bold text-slate-900">NLAMS</span>
          </div>
          <Link to="/login">
            <Button size="sm">Sign In</Button>
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-6 py-20 text-center">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
          <div className="inline-flex items-center gap-2 bg-primary-50 text-primary-700 px-4 py-2 rounded-full text-sm font-medium mb-6">
            🇮🇳 Digital India Initiative
          </div>
          <h1 className="text-4xl md:text-6xl font-bold text-slate-900 leading-tight">
            National Land Acquisition<br />
            <span className="text-primary-600">& Management System</span>
          </h1>
          <p className="text-lg text-slate-500 mt-6 max-w-2xl mx-auto">
            Digitizing India's land acquisition lifecycle end-to-end — from project proposal to rehabilitation & resettlement. A transparent, data-driven platform for every stakeholder.
          </p>
          <div className="flex justify-center gap-4 mt-8">
            <Link to="/login">
              <Button size="lg">Get Started →</Button>
            </Link>
            <Link to="/about">
              <Button variant="outline" size="lg">Learn More</Button>
            </Link>
          </div>
        </motion.div>
      </section>

      {/* Features */}
      <section className="max-w-6xl mx-auto px-6 py-16">
        <h2 className="text-2xl font-bold text-center text-slate-900 mb-12">Platform Capabilities</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
            >
              <Card className="h-full hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="text-3xl mb-3">{f.icon}</div>
                  <h3 className="font-semibold text-slate-900 mb-2">{f.title}</h3>
                  <p className="text-sm text-slate-500">{f.description}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Stats */}
      <section className="bg-primary-600 text-white py-16">
        <div className="max-w-6xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {[
            { value: '10+', label: 'States' },
            { value: '15+', label: 'Active Projects' },
            { value: '₹2,500 Cr+', label: 'Total Investment' },
            { value: '6', label: 'Stakeholder Roles' },
          ].map((s, i) => (
            <div key={i}>
              <div className="text-3xl font-bold">{s.value}</div>
              <div className="text-primary-200 text-sm mt-1">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-200 py-8">
        <div className="max-w-6xl mx-auto px-6 text-center text-sm text-slate-400">
          NLAMS v1.0 • Built for Smart India Hackathon 2025 • Sandbox/Demo Mode
        </div>
      </footer>
    </div>
  );
}
