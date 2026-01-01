// @ts-nocheck
import React from 'react';
import { useUserRole } from '../hooks/useUserRole';

export const UserRoleBadge: React.FC = () => {
  const { role, isSuperAdmin, isLoading } = useUserRole();

  if (isLoading) return null;

  return (
    <div className="fixed top-4 right-4 z-50">
      <div className={`px-4 py-2 rounded-full text-sm font-semibold shadow-lg ${
        isSuperAdmin 
          ? 'bg-purple-600 text-white' 
          : 'bg-blue-600 text-white'
      }`}>
        {isSuperAdmin ? '🛡️ SuperAdmin' : '👤 Customer User'}
      </div>
    </div>
  );
};
