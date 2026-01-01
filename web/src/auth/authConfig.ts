import type { Configuration, PopupRequest } from "@azure/msal-browser";

// Config object to be passed to Msal on creation
export const msalConfig: Configuration = {
    auth: {
        clientId: "257a158a-c6d6-4595-8dc3-df07e83504ac",
        authority: "https://login.microsoftonline.com/19815b28-437b-405b-ade0-daea9943eb8b",
        redirectUri: "https://fredesa-ai-platform.vercel.app",
        postLogoutRedirectUri: "https://fredesa-ai-platform.vercel.app",
    },
    cache: {
        cacheLocation: "localStorage", // Changed from sessionStorage for popup mode
        storeAuthStateInCookie: false,
    },
};

// Add here scopes for id token to be used at MS Identity Platform endpoints.
export const loginRequest: PopupRequest = {
    scopes: ["api://257a158a-c6d6-4595-8dc3-df07e83504ac/access_as_user"]
};

// Add here the endpoints for MS Graph API services you would like to use.
export const graphConfig = {
    graphMeEndpoint: "https://graph.microsoft.com/v1.0/me"
};
