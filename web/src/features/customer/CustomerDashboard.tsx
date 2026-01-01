// @ts-nocheck
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useMsal } from '@azure/msal-react';
import { getProposals, getUserProfile } from '../../api/client';

export const CustomerDashboard: React.FC = () => {
  const { instance } = useMsal();

  // Fetch user profile
  const { data: profile, isLoading: profileLoading } = useQuery({
    queryKey: ['userProfile'],
    queryFn: () => getUserProfile(instance),
  });

  // Fetch proposals
  const { data: proposals, isLoading: proposalsLoading, error } = useQuery({
    queryKey: ['proposals'],
    queryFn: () => getProposals(instance),
  });

  const isLoading = profileLoading || proposalsLoading;

  if (isLoading) {
    return (
      <div className="p-8 bg-white min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-slate-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 bg-white min-h-screen flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <h3 className="text-red-800 font-semibold mb-2">⚠️ Connection Error</h3>
          <p className="text-red-600 text-sm">Unable to load data from API. Please check your connection.</p>
        </div>
      </div>
    );
  }

  const activeProposals = proposals?.filter(p => p.status === 'active') || [];
  const totalProposals = proposals?.length || 0;

  return (
    <div className="p-8 bg-white min-h-screen">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">
              👋 Welcome back, {profile?.displayName || 'User'}
            </h1>
            <p className="text-slate-600">Manage your Federal Proposals and AI Agents</p>
          </div>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors">
            + New Proposal
          </button>
        </header>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-xl border border-blue-200">
            <h3 className="text-sm font-medium text-blue-600 uppercase">Total Proposals</h3>
            <p className="text-3xl font-bold text-blue-900 mt-2">{totalProposals}</p>
          </div>
          
          <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 p-6 rounded-xl border border-emerald-200">
            <h3 className="text-sm font-medium text-emerald-600 uppercase">Active</h3>
            <p className="text-3xl font-bold text-emerald-900 mt-2">{activeProposals.length}</p>
          </div>

          <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-xl border border-purple-200">
            <h3 className="text-sm font-medium text-purple-600 uppercase">Win Rate</h3>
            <p className="text-3xl font-bold text-purple-900 mt-2">
              {totalProposals > 0 ? Math.round((activeProposals.length / totalProposals) * 100) : 0}%
            </p>
          </div>
        </div>

        {/* Proposals List */}
        <div className="border border-slate-200 rounded-xl overflow-hidden">
          <div className="bg-slate-50 px-6 py-4 border-b border-slate-200">
            <h2 className="text-xl font-semibold">📋 Your Proposals</h2>
          </div>
          
          {proposals && proposals.length > 0 ? (
            <div className="divide-y divide-slate-100">
              {proposals.map((proposal) => (
                <div key={proposal.id} className="p-6 hover:bg-slate-50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-lg text-slate-900 mb-1">
                        {proposal.title}
                      </h3>
                      <p className="text-sm text-slate-600 mb-3">
                        {proposal.customer} • {proposal.agency}
                      </p>
                      <div className="flex items-center gap-4">
                        <span className={`text-xs px-3 py-1 rounded-full font-medium ${
                          proposal.status === 'active' 
                            ? 'bg-green-100 text-green-700' 
                            : proposal.status === 'pending'
                            ? 'bg-yellow-100 text-yellow-700'
                            : 'bg-slate-100 text-slate-600'
                        }`}>
                          {proposal.status.charAt(0).toUpperCase() + proposal.status.slice(1)}
                        </span>
                        <span className="text-xs text-slate-500">
                          Due: {new Date(proposal.dueDate).toLocaleDateString()}
                        </span>
                        <span className="text-xs font-semibold text-blue-600">
                          ${proposal.value.toLocaleString()}
                        </span>
                      </div>
                    </div>
                    <button className="ml-4 text-sm text-blue-600 hover:text-blue-700 font-medium">
                      View Details →
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-12 text-center">
              <p className="text-slate-400 text-lg">No proposals yet</p>
              <p className="text-slate-500 text-sm mt-2">Create your first proposal to get started</p>
            </div>
          )}
        </div>

        {/* API Connection Status */}
        <div className="mt-6 text-center">
          <p className="text-xs text-green-600 flex items-center justify-center gap-2">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
            Connected to FreDeSa API
          </p>
        </div>
      </div>
    </div>
  );
};
