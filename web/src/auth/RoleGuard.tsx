import React from 'react';
import { useIsAuthenticated, useMsal } from "@azure/msal-react";
import { Navigate, useLocation } from "react-router-dom";

interface RoleGuardProps {
    children: React.ReactNode;
    requiredRole?: 'FreDeSa_SuperAdmin' | 'Customer_User';
}

export const RoleGuard: React.FC<RoleGuardProps> = ({ children, requiredRole }) => {
    const isAuthenticated = useIsAuthenticated();
    const { instance } = useMsal();
    const location = useLocation();

    if (!isAuthenticated) {
        // Redirect to login page, but save the current location they were trying to go to
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    // -------------------------------------------------------------------------
    // 🔐 ENTERPRISE ROLE CHECK
    // -------------------------------------------------------------------------
    const accounts = instance.getAllAccounts();
    const activeAccount = accounts[0];
    
    // Extract roles from Azure AD ID Token claims
    const userRoles = (activeAccount?.idTokenClaims as any)?.roles || [];
    
    // Check if user has required role
    if (requiredRole && !userRoles.includes(requiredRole)) {
        console.warn(`Access denied: User lacks required role '${requiredRole}'`);
        console.log('User roles:', userRoles);
        return <Navigate to="/dashboard" replace />;  // Redirect to customer dashboard
    }

    return <>{children}</>;
};
