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
    // In a real scenario, we extract the role from the ID Token Claims.
    // For this prototype, we will simulate it or allow all authenticated users.
    
    const accounts = instance.getAllAccounts();
    const activeAccount = accounts[0];
    
    // Mock logic: In production, this comes from activeAccount.idTokenClaims.roles
    // const userRoles = (activeAccount?.idTokenClaims as any)?.roles || [];
    
    // if (requiredRole && !userRoles.includes(requiredRole)) {
    //    return <Navigate to="/unauthorized" />;
    // }

    return <>{children}</>;
};
