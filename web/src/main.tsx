import { StrictMode, useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { PublicClientApplication } from "@azure/msal-browser";
import { msalConfig } from "./auth/authConfig";
import './index.css'
import App from './App.tsx'

const rootElement = document.getElementById('root')!;
const root = createRoot(rootElement);

const RootComponent = () => {
  const [isInitialized, setIsInitialized] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [msalInstance] = useState(() => new PublicClientApplication(msalConfig));

  useEffect(() => {
    const init = async () => {
      try {
        await msalInstance.initialize();
        setIsInitialized(true);
      } catch (err: any) {
        console.error("MSAL Initialization Failed:", err);
        setError(err.message || "Unknown error during initialization");
      }
    };
    init();
  }, [msalInstance]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-red-50 text-red-900 p-6">
        <div className="max-w-2xl text-center">
          <h1 className="text-3xl font-bold mb-4">⚠️ Authentication Error</h1>
          <p className="text-lg mb-6">Unable to initialize Azure AD authentication.</p>
          <div className="bg-red-100 border border-red-200 rounded-lg p-4 mb-6">
            <pre className="text-left text-sm overflow-auto whitespace-pre-wrap text-red-800">
              {error}
            </pre>
          </div>
          <div className="text-sm text-red-700">
            <p className="font-semibold mb-2">Possible causes:</p>
            <ul className="text-left list-disc list-inside space-y-1">
              <li>Azure AD app registration not configured</li>
              <li>Redirect URI mismatch (must be http://localhost:3000)</li>
              <li>Client ID or Tenant ID incorrect</li>
              <li>Browser cache contains old authentication state</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }

  if (!isInitialized) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 text-slate-600">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-lg font-medium">Loading FreDeSa Platform...</p>
          <p className="text-sm text-slate-400 mt-2">Initializing authentication...</p>
        </div>
      </div>
    );
  }

  return (
    <StrictMode>
      <App pca={msalInstance} />
    </StrictMode>
  );
};

root.render(<RootComponent />);
