// @ts-nocheck
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useMsal } from '@azure/msal-react';
import { getUsers, getAnalytics } from '../../api/client';

export const AdminDashboard: React.FC = () => {
  const { instance } = useMsal();

  // Fetch analytics
  const { data: analytics, isLoading: analyticsLoading } = useQuery({
    queryKey: ['analytics'],
    queryFn: () => getAnalytics(instance as any),
  });

  // Fetch users
  const { data: users, isLoading: usersLoading, error } = useQuery({
    queryKey: ['users'],
    queryFn: () => getUsers(instance as any),
  });

  const isLoading = analyticsLoading || usersLoading;

  if (isLoading) {
    return (
      <div className="p-8 bg-slate-50 min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-slate-600">Loading admin dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 bg-slate-50 min-h-screen flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <h3 className="text-red-800 font-semibold mb-2">⚠️ Access Error</h3>
          <p className="text-red-600 text-sm">
            Unable to load admin data. Ensure you have FreDeSa_SuperAdmin role.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="max-w-7xl mx-auto p-8">
        {/* Header */}
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-slate-900 mb-2">
            🛡️ Admin Dashboard
          </h1>
          <p className="text-slate-600 text-lg">Platform Analytics and User Management</p>
        </header>

        {/* Analytics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-6 mb-8">
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <h3 className="text-sm font-semibold text-blue-600 uppercase tracking-wide mb-3">Total Proposals</h3>
            <p className="text-4xl font-bold text-slate-900">{analytics?.total_proposals || 0}</p>
          </div>
          
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <h3 className="text-sm font-semibold text-emerald-600 uppercase tracking-wide mb-3">Active Users</h3>
            <p className="text-4xl font-bold text-slate-900">{analytics?.active_users || 0}</p>
          </div>

          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <h3 className="text-sm font-semibold text-purple-600 uppercase tracking-wide mb-3">This Month</h3>
            <p className="text-4xl font-bold text-slate-900">{analytics?.proposals_this_month || 0}</p>
          </div>

          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <h3 className="text-sm font-semibold text-amber-600 uppercase tracking-wide mb-3">Completion Rate</h3>
            <p className="text-4xl font-bold text-slate-900">{analytics?.avg_completion_rate || 0}%</p>
          </div>

          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <h3 className="text-sm font-semibold text-cyan-600 uppercase tracking-wide mb-3">Contract Value</h3>
            <p className="text-3xl font-bold text-slate-900">{analytics?.total_contract_value || '$0'}</p>
          </div>

          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <h3 className="text-sm font-semibold text-rose-600 uppercase tracking-wide mb-3">Win Rate</h3>
            <p className="text-4xl font-bold text-slate-900">{analytics?.win_rate || 0}%</p>
          </div>
        </div>

        {/* Users Table */}
        <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
          <div className="bg-gradient-to-r from-slate-100 to-slate-50 px-6 py-4 border-b border-slate-200">
            <h2 className="text-2xl font-bold text-slate-900">👥 User Management</h2>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700 uppercase tracking-wide">User</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700 uppercase tracking-wide">Email</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700 uppercase tracking-wide">Role</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700 uppercase tracking-wide">Status</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700 uppercase tracking-wide">Last Login</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700 uppercase tracking-wide">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {users?.users?.map((user) => (
                  <tr key={user.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                          <span className="text-lg font-bold text-blue-600">{user.name.charAt(0)}</span>
                        </div>
                        <span className="font-semibold text-slate-900">{user.name}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-slate-600">{user.email}</td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        user.role === 'FreDeSa_SuperAdmin' 
                          ? 'bg-purple-100 text-purple-700 border border-purple-200' 
                          : 'bg-blue-100 text-blue-700 border border-blue-200'
                      }`}>
                        {user.role.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        user.status === 'active' 
                          ? 'bg-emerald-100 text-emerald-700 border border-emerald-200' 
                          : 'bg-slate-100 text-slate-600 border border-slate-200'
                      }`}>
                        {user.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-600 text-sm">
                      {new Date(user.last_login).toLocaleString()}
                    </td>
                    <td className="px-6 py-4">
                      <button className="text-blue-600 hover:text-blue-700 font-medium text-sm">
                        Edit
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* API Connection Status */}
        <div className="mt-8 flex items-center justify-center">
          <div className="bg-white border border-emerald-200 rounded-full px-4 py-2 shadow-sm">
            <p className="text-sm text-emerald-700 font-medium flex items-center gap-2">
              <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
              Connected to FreDeSa API
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
