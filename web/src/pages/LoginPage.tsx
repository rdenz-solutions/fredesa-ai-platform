import React, { useEffect } from 'react';
import { useMsal, useIsAuthenticated } from "@azure/msal-react";
import { loginRequest } from "../auth/authConfig";
import { Navigate, useNavigate } from 'react-router-dom';

export const LoginPage: React.FC = () => {
  const { instance } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const navigate = useNavigate();
  const [isLoggingIn, setIsLoggingIn] = React.useState(false);
  const [loginError, setLoginError] = React.useState<string | null>(null);

  // 🔑 If already authenticated, redirect immediately
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleLogin = async () => {
    setIsLoggingIn(true);
    setLoginError(null);
    try {
      await instance.loginPopup(loginRequest);
      // After successful login, navigate to home (SmartRedirect will handle role routing)
      navigate('/', { replace: true });
    } catch (e: any) {
      console.error('Login failed:', e);
      setLoginError(e.message || 'Login failed. Please try again.');
      setIsLoggingIn(false);
    }
  };

  // Show loading state if authenticated (during redirect)
  if (isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900">
        <div className="text-white text-center">
          <div className="w-12 h-12 border-4 border-white border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p>Redirecting to dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900">
      <div className="bg-white p-8 rounded-2xl shadow-2xl max-w-md w-full text-center">
        <div className="mb-6">
            <div className="w-16 h-16 bg-blue-600 rounded-xl mx-auto flex items-center justify-center text-white text-2xl font-bold mb-4">
                F
            </div>
            <h1 className="text-2xl font-bold text-slate-900">Sign in to FreDeSa</h1>
            <p className="text-slate-500 mt-2">Enterprise AI Orchestration Platform</p>
        </div>

        {loginError && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {loginError}
          </div>
        )}

        <button 
            onClick={handleLogin}
            disabled={isLoggingIn}
            className="w-full bg-slate-900 text-white py-3 px-4 rounded-lg font-medium hover:bg-slate-800 transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
            {isLoggingIn ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Signing in...
              </>
            ) : (
              <>
                <svg className="w-5 h-5" viewBox="0 0 23 23" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path fill="#f3f3f3" d="M0 0h23v23H0z"/>
                    <path fill="#f35325" d="M1 1h10v10H1z"/>
                    <path fill="#81bc06" d="M12 1h10v10H12z"/>
                    <path fill="#05a6f0" d="M1 12h10v10H1z"/>
                    <path fill="#ffba08" d="M12 12h10v10H12z"/>
                </svg>
                Sign in with Microsoft
              </>
            )}
        </button>

        <p className="mt-6 text-xs text-slate-400">
            Authorized Federal Contractors & Personnel Only.
            <br/>
            Protected by Azure Entra ID.
        </p>
      </div>
    </div>
  );
};
