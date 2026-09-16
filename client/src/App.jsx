import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { TourProvider } from './context/TourContext';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { ProductTourOfferModal } from './components/ProductTourOfferModal';
import { AppTourModal } from './components/AppTourModal';

// Pages
import { Dashboard } from './pages/Dashboard';
import { Profile } from './pages/Profile';
import { Assessment } from './pages/Assessment';
import { JobExplorer } from './pages/JobExplorer';
import { JobDetails } from './pages/JobDetails';
import { LearningPlan } from './pages/LearningPlan';
import { Tailoring } from './pages/Tailoring';
import { Applications } from './pages/Applications';
import { InterviewPrep } from './pages/InterviewPrep';
import { Analytics } from './pages/Analytics';
import { Login } from './pages/Login';
import { Register } from './pages/Register';

const Layout = ({ children }) => {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <Navbar />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-6 lg:p-8 max-w-7xl mx-auto w-full overflow-x-hidden">
          {children}
        </main>
      </div>
    </div>
  );
};

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-brand-500"></div>
      </div>
    );
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return <Layout>{children}</Layout>;
};

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <TourProvider>
          {/* Automatic Product Tour Offer & Interactive Tour Modals mounted at app root */}
          <ProductTourOfferModal />
          <AppTourModal />

          <Routes>
            {/* Public Auth Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Protected Application Routes */}
            <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
            <Route path="/assessment" element={<ProtectedRoute><Assessment /></ProtectedRoute>} />
            <Route path="/jobs" element={<ProtectedRoute><JobExplorer /></ProtectedRoute>} />
            <Route path="/jobs/:jobId" element={<ProtectedRoute><JobDetails /></ProtectedRoute>} />
            <Route path="/learning" element={<ProtectedRoute><LearningPlan /></ProtectedRoute>} />
            <Route path="/tailoring" element={<ProtectedRoute><Tailoring /></ProtectedRoute>} />
            <Route path="/applications" element={<ProtectedRoute><Applications /></ProtectedRoute>} />
            <Route path="/interview" element={<ProtectedRoute><InterviewPrep /></ProtectedRoute>} />
            <Route path="/analytics" element={<ProtectedRoute><Analytics /></ProtectedRoute>} />

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </TourProvider>
      </BrowserRouter>
    </AuthProvider>
  );
}
