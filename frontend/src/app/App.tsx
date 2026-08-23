import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from '../store/AuthContext';
import { RoleShell } from '../components/layout/RoleShell';

// Auth pages
import Login from '../pages/auth/Login';

// Admin pages
import NationalDashboard from '../pages/admin/NationalDashboard';
import ProjectList from '../pages/admin/ProjectList';
import ProjectDetail from '../pages/admin/ProjectDetail';
import UserManagement from '../pages/admin/UserManagement';
import ReportsPage from '../pages/admin/ReportsPage';
import GISMapPage from '../pages/admin/GISMapPage';
import NotificationsPage from '../pages/admin/NotificationsPage';

// State pages
import StateDashboard from '../pages/state/StateDashboard';

// District pages
import DistrictDashboard from '../pages/district/DistrictDashboard';

// Agency pages
import MyProjects from '../pages/agency/MyProjects';

// Field pages
import MobileSurveys from '../pages/field/MobileSurveys';

// Citizen pages
import TrackStatus from '../pages/citizen/TrackStatus';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth();
  if (isLoading) return <div className="min-h-screen flex items-center justify-center"><div className="skeleton h-8 w-32 rounded" /></div>;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function RoleRedirect() {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;

  const roleRoutes: Record<string, string> = {
    super_admin: '/admin/dashboard',
    state_authority: '/state/dashboard',
    district_officer: '/district/dashboard',
    agency: '/agency/projects',
    field_officer: '/field/surveys',
    citizen: '/citizen/track',
  };

  return <Navigate to={roleRoutes[user.role_name] || '/admin/dashboard'} replace />;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      {/* Admin routes */}
      <Route path="/admin" element={<ProtectedRoute><RoleShell /></ProtectedRoute>}>
        <Route path="dashboard" element={<NationalDashboard />} />
        <Route path="projects" element={<ProjectList />} />
        <Route path="projects/:id" element={<ProjectDetail />} />
        <Route path="users" element={<UserManagement />} />
        <Route path="reports" element={<ReportsPage />} />
        <Route path="gis" element={<GISMapPage />} />
        <Route path="notifications" element={<NotificationsPage />} />
      </Route>

      {/* State routes */}
      <Route path="/state" element={<ProtectedRoute><RoleShell /></ProtectedRoute>}>
        <Route path="dashboard" element={<StateDashboard />} />
        <Route path="projects" element={<ProjectList />} />
        <Route path="projects/:id" element={<ProjectDetail />} />
        <Route path="gis" element={<GISMapPage />} />
        <Route path="reports" element={<ReportsPage />} />
        <Route path="notifications" element={<NotificationsPage />} />
      </Route>

      {/* District routes */}
      <Route path="/district" element={<ProtectedRoute><RoleShell /></ProtectedRoute>}>
        <Route path="dashboard" element={<DistrictDashboard />} />
        <Route path="verification" element={<ProjectList />} />
        <Route path="parcels" element={<GISMapPage />} />
        <Route path="compensation" element={<ReportsPage />} />
        <Route path="notifications" element={<NotificationsPage />} />
      </Route>

      {/* Agency routes */}
      <Route path="/agency" element={<ProtectedRoute><RoleShell /></ProtectedRoute>}>
        <Route path="projects" element={<MyProjects />} />
        <Route path="projects/:id" element={<ProjectDetail />} />
        <Route path="gis" element={<GISMapPage />} />
        <Route path="documents" element={<ReportsPage />} />
      </Route>

      {/* Field Officer routes */}
      <Route path="/field" element={<ProtectedRoute><RoleShell /></ProtectedRoute>}>
        <Route path="home" element={<MobileSurveys />} />
        <Route path="surveys" element={<MobileSurveys />} />
        <Route path="camera" element={<MobileSurveys />} />
        <Route path="profile" element={<MobileSurveys />} />
      </Route>

      {/* Citizen routes */}
      <Route path="/citizen" element={<ProtectedRoute><RoleShell /></ProtectedRoute>}>
        <Route path="track" element={<TrackStatus />} />
        <Route path="compensation" element={<TrackStatus />} />
        <Route path="documents" element={<TrackStatus />} />
        <Route path="notifications" element={<NotificationsPage />} />
      </Route>

      {/* Root redirect */}
      <Route path="/" element={<RoleRedirect />} />
      <Route path="*" element={<RoleRedirect />} />
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}
