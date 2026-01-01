import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { MsalProvider, useMsal, useIsAuthenticated } from "@azure/msal-react";
import type { IPublicClientApplication } from "@azure/msal-browser";
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { RoleGuard } from './auth/RoleGuard';
import { MainLayout } from './layouts/MainLayout';
import { LoginPage } from './pages/LoginPage';
import { AdminDashboard } from './features/admin/AdminDashboard';
import { CustomerDashboard } from './features/customer/CustomerDashboard';

// Initialize React Query
const queryClient = new QueryClient();

// -----------------------------------------------------------------------------
// 🧠 SMART ROUTER: Decides where to send the user based on role
// -----------------------------------------------------------------------------
const SmartRedirect: React.FC = () => {
    const { instance } = useMsal();
    const isAuthenticated = useIsAuthenticated();

    if (!isAuthenticated) {
        return <Navigate to="/login" />;
    }

    // Mock Role Logic (Replace with real claims check)
    // const role = instance.getAllAccounts()[0]?.idTokenClaims?.roles?.[0];
    const role = "Customer_User"; // Default for now

    if (role === 'FreDeSa_SuperAdmin') {
        return <Navigate to="/admin" />;
    }
    
    return <Navigate to="/dashboard" />;
};

interface AppProps {
    pca: IPublicClientApplication;
}

const App: React.FC<AppProps> = ({ pca }) => {
  return (
    <MsalProvider instance={pca}>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<LoginPage />} />

            {/* Protected Routes (Wrapped in MainLayout) */}
            <Route element={<MainLayout />}>
                {/* Root redirects intelligently */}
                <Route path="/" element={<SmartRedirect />} />

                {/* Admin Routes */}
                <Route path="/admin" element={
                    <RoleGuard requiredRole="FreDeSa_SuperAdmin">
                        <AdminDashboard />
                    </RoleGuard>
                } />

                {/* Customer Routes */}
                <Route path="/dashboard" element={
                    <RoleGuard requiredRole="Customer_User">
                        <CustomerDashboard />
                    </RoleGuard>
                } />
            </Route>
          </Routes>
        </BrowserRouter>
      </QueryClientProvider>
    </MsalProvider>
  );
};

export default App;
