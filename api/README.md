# Backend API Setup Instructions

## Quick Start

### 1. Install Python Dependencies
```bash
cd api
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set Up Environment Variables
```bash
cp .env.example .env
# Edit .env if needed (defaults are already configured)
```

### 3. Start the Backend Server
```bash
python main.py
```

The API will be running at `http://localhost:8000`

### 4. Test the API
```bash
# Health check
curl http://localhost:8000/health

# API docs (interactive)
open http://localhost:8000/docs
```

## Architecture

**Authentication Flow:**
1. User logs in via React frontend (Azure AD)
2. Frontend receives JWT token from Azure
3. Frontend sends token in Authorization header: `Bearer <token>`
4. Backend validates token with Azure AD
5. Backend extracts user info and role
6. Backend returns data based on user permissions

**Endpoints:**
- `GET /` - Health check
- `GET /api/user/profile` - Get current user info
- `GET /api/proposals` - List proposals
- `GET /api/proposals/{id}` - Get proposal details
- `GET /api/admin/users` - List users (Admin only)
- `GET /api/admin/analytics` - Platform analytics (Admin only)

## Frontend Integration

The React frontend automatically:
- Acquires access tokens from MSAL
- Sends tokens in API requests
- Handles token refresh
- Shows user info from API

**API Client Usage:**
```typescript
import { getProposals } from './api/client';
import { useMsal } from "@azure/msal-react";

function MyComponent() {
  const { instance } = useMsal();
  
  const fetchData = async () => {
    const data = await getProposals(instance);
    console.log(data.proposals);
  };
}
```

## Development Workflow

**Terminal 1 - Backend:**
```bash
cd api
source venv/bin/activate
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd web
npm run dev
```

Both servers will auto-reload on file changes.

## Next Steps

1. **Add Database**: Replace mock data with PostgreSQL/MongoDB
2. **Add Real Business Logic**: Implement proposal creation, editing, etc.
3. **Deploy Backend**: Azure Container Apps or App Service
4. **Connect Services**: Update CORS and frontend API URL for production
