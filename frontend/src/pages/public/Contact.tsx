import React from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';

export default function Contact() {
  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="border-b border-slate-200 bg-white/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-primary-500 flex items-center justify-center text-white font-bold text-sm">N</div>
            <span className="font-bold text-slate-900">NLAMS</span>
          </Link>
          <Link to="/login"><Button size="sm">Sign In</Button></Link>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-6 py-16 space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Contact Us</h1>
          <p className="text-slate-500 mt-2">Get in touch with the NLAMS support team</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardContent className="p-6 space-y-4">
              <h3 className="font-semibold text-slate-900">📞 Helpline</h3>
              <div className="text-sm text-slate-600">
                <p>Toll-Free: <span className="font-medium">1800-XXX-XXXX</span></p>
                <p>Email: <span className="font-medium">support@nlams.gov.in</span></p>
                <p>Hours: Mon-Sat, 9:00 AM — 6:00 PM</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6 space-y-4">
              <h3 className="font-semibold text-slate-900">🏛️ Nodal Office</h3>
              <div className="text-sm text-slate-600">
                <p>National Land Acquisition Authority</p>
                <p>Nirman Bhavan, New Delhi — 110011</p>
                <p>Ministry of Rural Development</p>
              </div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardContent className="p-6">
            <h3 className="font-semibold text-slate-900 mb-4">Send us a message</h3>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="contact-name" className="text-sm font-medium text-slate-700">Name</label>
                  <input id="contact-name" className="mt-1 w-full rounded-lg border border-slate-300 p-2 text-sm" placeholder="Your name" />
                </div>
                <div>
                  <label htmlFor="contact-email" className="text-sm font-medium text-slate-700">Email</label>
                  <input id="contact-email" type="email" className="mt-1 w-full rounded-lg border border-slate-300 p-2 text-sm" placeholder="your@email.com" />
                </div>
              </div>
              <div>
                <label htmlFor="contact-message" className="text-sm font-medium text-slate-700">Message</label>
                <textarea id="contact-message" className="mt-1 w-full rounded-lg border border-slate-300 p-3 text-sm" rows={4} placeholder="Your message..." />
              </div>
              <Button>Send Message</Button>
            </div>
          </CardContent>
        </Card>

        <div className="text-center text-xs text-slate-400 py-4">
          Sandbox/Demo Mode — SMS, email, and helpline integrations are simulated for hackathon demo purposes.
        </div>
      </div>
    </div>
  );
}
