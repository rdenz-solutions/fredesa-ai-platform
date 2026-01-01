/**
 * Custom hook to get user role from API
 */
import { useQuery } from '@tanstack/react-query';
import { useMsal } from '@azure/msal-react';
import { getUserProfile } from '../api/client';

export const useUserRole = () => {
  const { instance } = useMsal();

  const { data: profile, isLoading } = useQuery({
    queryKey: ['userProfile'],
    queryFn: () => getUserProfile(instance as any),
  });

  const role = profile?.role;
  const isSuperAdmin = role === 'FreDeSa_SuperAdmin';
  const isCustomerUser = role === 'Customer_User';

  return {
    role,
    isSuperAdmin,
    isCustomerUser,
    isLoading,
  };
};
