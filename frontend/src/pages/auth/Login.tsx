import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../store/AuthContext';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      // Navigate based on role stored in localStorage
      const user = JSON.parse(localStorage.getItem('nlams_user') || '{}');
      const roleRoutes: Record<string, string> = {
        super_admin: '/admin/dashboard',
        state_authority: '/state/dashboard',
        district_officer: '/district/dashboard',
        agency: '/agency/projects',
        field_officer: '/field/home',
        citizen: '/citizen/track',
      };
      navigate(roleRoutes[user.role_name] || '/admin/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  const quickLogin = async (email: string) => {
    setEmail(email);
    setPassword('password123');
    setError('');
    setLoading(true);
    try {
      await login(email, 'password123');
      const user = JSON.parse(localStorage.getItem('nlams_user') || '{}');
      const roleRoutes: Record<string, string> = {
        super_admin: '/admin/dashboard',
        state_authority: '/state/dashboard',
        district_officer: '/district/dashboard',
        agency: '/agency/projects',
        field_officer: '/field/home',
        citizen: '/citizen/track',
      };
      navigate(roleRoutes[user.role_name] || '/admin/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-900 via-primary-800 to-primary-700 flex items-center justify-center p-4">
      <div className="w-full max-w-md space-y-6">
        {/* Header */}
        <div className="text-center text-white space-y-2">
          <div className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm rounded-full px-4 py-2 text-sm">
            🇮🇳 Government of India Initiative
          </div>
          <h1 className="text-3xl font-bold">NLAMS</h1>
          <p className="text-primary-200 text-sm">National Land Acquisition & Management System</p>
        </div>

        {/* Login Card */}
        <Card className="border-0 shadow-2xl">
          <CardHeader className="text-center">
            <CardTitle>Sign In</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label htmlFor="login-email" className="text-sm font-medium text-slate-700">Email</label>
                <Input
                  id="login-email"
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-1.5">
                <label htmlFor="login-password" className="text-sm font-medium text-slate-700">Password</label>
                <Input
                  id="login-password"
                  type="password"
                  placeholder="Enter password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
              {error && (
                <div className="bg-red-50 text-red-700 text-sm rounded-lg p-3 border border-red-200">{error}</div>
              )}
              <div className="flex justify-end">
                <Link to="/forgot-password" className="text-xs text-primary-600 hover:underline">
                  Forgot Password?
                </Link>
              </div>
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? 'Signing in...' : 'Sign In'}
              </Button>
            </form>

            {/* Quick Login */}
            <div className="mt-6 border-t pt-4">
              <p className="text-xs text-slate-500 text-center mb-3">🚀 Quick Demo Login (password: password123)</p>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { label: '🔑 Super Admin', email: 'rajesh@nlams.gov.in' },
                  { label: '🏛️ State Authority', email: 'anil@maharashtra.gov.in' },
                  { label: '📋 District Officer', email: 'suresh@nagpur.gov.in' },
                  { label: '🏗️ Agency', email: 'agency@nhai.gov.in' },
                  { label: '📱 Field Officer', email: 'rahul.f@nlams.gov.in' },
                  { label: '👤 Citizen', email: 'ganesh@email.com' },
                ].map((item) => (
                  <Button
                    key={item.email}
                    variant="outline"
                    size="sm"
                    className="text-xs justify-start"
                    onClick={() => quickLogin(item.email)}
                    disabled={loading}
                  >
                    {item.label}
                  </Button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
