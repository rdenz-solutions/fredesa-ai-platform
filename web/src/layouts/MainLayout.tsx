import React from 'react';
import { useMsal, useIsAuthenticated } from "@azure/msal-react";
import { Link, Outlet, useNavigate, Navigate } from 'react-router-dom';
import { LogOut, User } from 'lucide-react';
import { UserRoleBadge } from '../components/UserRoleBadge';

export const MainLayout: React.FC = () => {
  const { instance, accounts } = useMsal();
  const navigate = useNavigate();
  const isAuthenticated = useIsAuthenticated();

  // 🔒 CRITICAL: Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  const handleLogout = () => {
      instance.logoutPopup({
          postLogoutRedirectUri: "/",
          mainWindowRedirectUri: "/"
      });
  };

  const user = accounts[0] || { name: "Guest User", username: "guest@example.com" };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Top Navigation Bar */}
      <nav className="bg-white border-b border-slate-200 px-6 py-3 flex justify-between items-center sticky top-0 z-50">
        <div className="flex items-center gap-8">
            <Link to="/" className="flex items-center gap-2">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">F</div>
                <span className="font-bold text-xl text-slate-900">FreDeSa</span>
            </Link>
            
            {/* Environment Badge (Visible in Dev/Staging) */}
            {import.meta.env.VITE_ENV_NAME !== 'production' && (
                <span className="px-2 py-1 bg-amber-100 text-amber-800 text-xs font-bold rounded uppercase border border-amber-200">
                    {import.meta.env.VITE_ENV_NAME || 'Development'} Environment
                </span>
            )}
        </div>

        <div className="flex items-center gap-4">
            <div className="flex items-center gap-3 px-3 py-1.5 rounded-full bg-slate-50 border border-slate-100">
                <div className="w-8 h-8 bg-slate-200 rounded-full flex items-center justify-center text-slate-600">
                    <User size={16} />
                </div>
                <div className="text-sm hidden md:block">
                    <p className="font-medium text-slate-900">{user.name}</p>
                    <p className="text-xs text-slate-500">{user.username}</p>
                </div>
            </div>
            
            <button 
                onClick={handleLogout}
                className="p-2 text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                title="Sign Out"
            >
                <LogOut size={20} />
            </button>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="flex-1">
        <UserRoleBadge />
        <Outlet />
      </main>
    </div>
  );
};
