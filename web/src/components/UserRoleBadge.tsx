// @ts-nocheck
import React from 'react';
import { useUserRole } from '../hooks/useUserRole';

export const UserRoleBadge: React.FC = () => {
  const { role, isSuperAdmin, isLoading } = useUserRole();

  if (isLoading) return null;

  return (
    <span className={`px-3 py-1 text-xs font-semibold rounded-full border ${
      isSuperAdmin 
        ? 'bg-purple-100 text-purple-700 border-purple-200' 
        : 'bg-blue-100 text-blue-700 border-blue-200'
    }`}>
      {isSuperAdmin ? '🛡️ SuperAdmin' : '👤 Customer User'}
    </span>
  );
};
