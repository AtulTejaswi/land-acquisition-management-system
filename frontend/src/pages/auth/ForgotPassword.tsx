import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { authService } from '../../services/auth';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    setStatus('loading');
    try {
      const result = await authService.forgotPassword(email);
      setStatus('success');
      setMessage(result.message || 'OTP sent to your registered email/phone. Check console for demo OTP.');
    } catch (err: any) {
      setStatus('error');
      setMessage(err?.response?.data?.detail || 'Email not found or service unavailable.');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2 mb-4">
            <div className="h-10 w-10 rounded-lg bg-primary-500 flex items-center justify-center text-white font-bold">N</div>
            <span className="font-bold text-xl text-slate-900">NLAMS</span>
          </Link>
        </div>

        <Card className="shadow-xl">
          <CardHeader>
            <CardTitle className="text-center">🔐 Forgot Password</CardTitle>
            <p className="text-sm text-slate-500 text-center">
              Enter your registered email to receive a password reset OTP
            </p>
          </CardHeader>
          <CardContent>
            {status === 'success' ? (
              <div className="text-center space-y-4">
                <div className="text-4xl">✅</div>
                <p className="text-sm text-emerald-700 bg-emerald-50 p-3 rounded-lg">
                  {message}
                </p>
                <p className="text-xs text-slate-500">
                  Sandbox/Demo Mode: In production, an OTP would be sent via SMS/email.
                </p>
                <Link to="/login">
                  <Button className="w-full">← Back to Login</Button>
                </Link>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label htmlFor="forgot-email" className="text-sm font-medium text-slate-700 mb-1 block">
                    Registered Email
                  </label>
                  <Input
                    id="forgot-email"
                    type="email"
                    placeholder="e.g. rajesh@nlams.gov.in"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </div>

                {status === 'error' && (
                  <p className="text-sm text-red-600 bg-red-50 p-2 rounded-lg">{message}</p>
                )}

                <Button type="submit" className="w-full" disabled={status === 'loading'}>
                  {status === 'loading' ? 'Sending OTP...' : 'Send Reset OTP'}
                </Button>

                <div className="text-center">
                  <Link to="/login" className="text-sm text-primary-600 hover:underline">
                    ← Back to Login
                  </Link>
                </div>
              </form>
            )}

            <div className="mt-6 p-3 bg-amber-50 border border-amber-200 rounded-lg">
              <p className="text-xs text-amber-700">
                <strong>Sandbox/Demo Mode:</strong> This is a mock OTP flow. In production,
                the OTP would be sent via the configured SMS/email gateway.
              </p>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
