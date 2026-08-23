import React from 'react';
import { Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { AuthProvider, useAuth } from '../store/AuthContext';
import { RoleShell } from '../components/layout/RoleShell';
import { ToastProvider } from '../components/toast/ToastProvider';

// Auth
import Login from '../pages/auth/Login';

// Public
import Landing from '../pages/public/Landing';
import About from '../pages/public/About';
import Contact from '../pages/public/Contact';

// Admin
import NationalDashboard from '../pages/admin/NationalDashboard';
import ProjectList from '../pages/admin/ProjectList';
import ProjectDetail from '../pages/admin/ProjectDetail';
import UserManagement from '../pages/admin/UserManagement';
import ReportsPage from '../pages/admin/ReportsPage';
import GISMapPage from '../pages/admin/GISMapPage';
import NotificationsPage from '../pages/admin/NotificationsPage';

// State
import StateDashboard from '../pages/state/StateDashboard';

// District
import DistrictDashboard from '../pages/district/DistrictDashboard';

// Agency
import MyProjects from '../pages/agency/MyProjects';
import CreateProposal from '../pages/agency/CreateProposal';

// Field
import MobileHome from '../pages/field/MobileHome';
import MobileSurveys from '../pages/field/MobileSurveys';
import MobileCamera from '../pages/field/MobileCamera';
import MobileProfile from '../pages/field/MobileProfile';

// Citizen
import TrackStatus from '../pages/citizen/TrackStatus';
import MyCompensation from '../pages/citizen/MyCompensation';
import MyDocuments from '../pages/citizen/MyDocuments';

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
    field_officer: '/field/home',
    citizen: '/citizen/track',
  };
  return <Navigate to={roleRoutes[user.role_name] || '/admin/dashboard'} replace />;
}

function AppRoutes() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/" element={<Landing />} />
      <Route path="/about" element={<About />} />
      <Route path="/contact" element={<Contact />} />
      <Route path="/login" element={<Login />} />

      {/* Admin */}
      <Route path="/admin" element={<ProtectedRoute><RoleShell /></ProtectedRoute>}>
        <Route path="dashboard" element={<NationalDashboard />} />
        <Route path="projects" element={<ProjectList />} />
        <Route path="projects/:id" element={<ProjectDetail />} />
        <Route path="users" element={<UserManagement />} />
        <Route path="reports" element={<ReportsPage />} />
        <Route path="gis" element={<GISMapPage />} />
        <Route path="notifications" element={<NotificationsPage />} />
      </Route>

      {/* State */}
      <Route path="/state" element={<ProtectedRoute><RoleShell /></ProtectedRoute>}>
        <Route path="dashboard" element={<StateDashboard />} />
        <Route path="projects" element={<ProjectList />} />
        <Route path="projects/:id" element={<ProjectDetail />} />
        <Route path="gis" element={<GISMapPage />} />
        <Route path="reports" element={<ReportsPage />} />
        <Route path="notifications" element={<NotificationsPage />} />
      </Route>

      {/* District */}
      <Route path="/district" element={<ProtectedRoute><RoleShell /></ProtectedRoute>}>
        <Route path="dashboard" element={<DistrictDashboard />} />
        <Route path="verification" element={<ProjectList />} />
        <Route path="parcels" element={<GISMapPage />} />
        <Route path="compensation" element={<ReportsPage />} />
        <Route path="notifications" element={<NotificationsPage />} />
      </Route>

      {/* Agency */}
      <Route path="/agency" element={<ProtectedRoute><RoleShell /></ProtectedRoute>}>
        <Route path="projects" element={<MyProjects />} />
        <Route path="create" element={<CreateProposal />} />
        <Route path="projects/:id" element={<ProjectDetail />} />
        <Route path="gis" element={<GISMapPage />} />
        <Route path="documents" element={<ReportsPage />} />
      </Route>

      {/* Field Officer */}
      <Route path="/field" element={<ProtectedRoute><RoleShell /></ProtectedRoute>}>
        <Route path="home" element={<MobileHome />} />
        <Route path="surveys" element={<MobileSurveys />} />
        <Route path="camera" element={<MobileCamera />} />
        <Route path="profile" element={<MobileProfile />} />
      </Route>

      {/* Citizen */}
      <Route path="/citizen" element={<ProtectedRoute><RoleShell /></ProtectedRoute>}>
        <Route path="track" element={<TrackStatus />} />
        <Route path="compensation" element={<MyCompensation />} />
        <Route path="documents" element={<MyDocuments />} />
        <Route path="notifications" element={<NotificationsPage />} />
      </Route>

      {/* Catch-all */}
      <Route path="*" element={<RoleRedirect />} />
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <AppRoutes />
      </ToastProvider>
    </AuthProvider>
  );
}
