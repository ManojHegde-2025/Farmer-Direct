import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import { Navbar } from './components/layout/Navbar';
import { Footer } from './components/layout/Footer';

// Pages
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/auth/LoginPage';
import { RegisterPage } from './pages/auth/RegisterPage';
import { MarketplacePage } from './pages/marketplace/MarketplacePage';
import { ListingDetailPage } from './pages/marketplace/ListingDetailPage';

// Farmer Pages
import { FarmerDashboard } from './pages/farmer/FarmerDashboard';
import { CreateListingPage } from './pages/farmer/CreateListingPage';

// Buyer Pages
import { BuyerDashboard } from './pages/buyer/BuyerDashboard';
import { CreateRequirementPage } from './pages/buyer/CreateRequirementPage';
import { BuyerMatchesPage } from './pages/buyer/BuyerMatchesPage';

// Admin Pages
import { AdminDashboard } from './pages/admin/AdminDashboard';

// Messaging Page
import { MessagesPage } from './pages/messages/MessagesPage';

// Protected Route Guard
const ProtectedRoute: React.FC<{ children: React.ReactNode; allowedRoles?: string[] }> = ({
  children,
  allowedRoles,
}) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 text-slate-500 text-sm">
        Verifying authorization...
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role) && user.role !== 'ADMIN') {
    return <Navigate to="/marketplace" replace />;
  }

  return <>{children}</>;
};

export const App: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Navbar />
      <main className="flex-1">
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/marketplace" element={<MarketplacePage />} />
          <Route path="/marketplace/:id" element={<ListingDetailPage />} />

          {/* Farmer Routes */}
          <Route
            path="/farmer/dashboard"
            element={
              <ProtectedRoute allowedRoles={['FARMER']}>
                <FarmerDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/farmer/create-listing"
            element={
              <ProtectedRoute allowedRoles={['FARMER']}>
                <CreateListingPage />
              </ProtectedRoute>
            }
          />

          {/* Buyer Routes */}
          <Route
            path="/buyer/dashboard"
            element={
              <ProtectedRoute allowedRoles={['BUYER']}>
                <BuyerDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/buyer/create-requirement"
            element={
              <ProtectedRoute allowedRoles={['BUYER']}>
                <CreateRequirementPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/buyer/matches/:reqId"
            element={
              <ProtectedRoute allowedRoles={['BUYER']}>
                <BuyerMatchesPage />
              </ProtectedRoute>
            }
          />

          {/* Admin Routes */}
          <Route
            path="/admin/dashboard"
            element={
              <ProtectedRoute allowedRoles={['ADMIN']}>
                <AdminDashboard />
              </ProtectedRoute>
            }
          />

          {/* Private Messaging Route */}
          <Route
            path="/messages"
            element={
              <ProtectedRoute allowedRoles={['FARMER', 'BUYER', 'ADMIN']}>
                <MessagesPage />
              </ProtectedRoute>
            }
          />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
};
