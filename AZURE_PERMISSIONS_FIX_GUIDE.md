# Azure Permissions Fix Guide
**Date**: January 3, 2026  
**Issue**: SandraEstok@FredesaLLC.onmicrosoft.com lacks permissions to view Azure resources  
**Status**: Requires Owner/Administrator action

---

## 🎯 Problem Summary

**Current Situation**:
- ✅ Azure CLI installed and authenticated
- ✅ Account: `SandraEstok@FredesaLLC.onmicrosoft.com`
- ✅ Subscription: MCPP Subscription (`c99bdba1-68a6-4dde-afa8-2f437ba8dd22`)
- ❌ **Missing**: Reader permissions on resource group `fredesa-rg`

**Error Messages**:
```
AuthorizationFailed: The client 'SandraEstok@FredesaLLC.onmicrosoft.com' 
does not have authorization to perform action 
'Microsoft.Resources/subscriptions/resourcegroups/read' 
over scope '/subscriptions/.../resourcegroups/fredesa-rg'
```

---

## 🔧 Solution: Assign Reader Role

### **Who Can Fix This**:
Only users with one of these roles can assign permissions:
- **Owner** (full control)
- **User Access Administrator** (can manage access)
- **Subscription Administrator** (legacy role)

### **Recommended User**: 
Someone with **Owner** role on the subscription or resource group `fredesa-rg`

---

## 📋 Step-by-Step Fix

### **Option 1: Azure Portal** (Easiest)

1. **Sign in to Azure Portal**
   - Go to: https://portal.azure.com
   - Sign in with an account that has Owner/Administrator role

2. **Navigate to Resource Group**
   - Search for "Resource groups"
   - Click on `fredesa-rg`

3. **Assign Role**
   - Click "Access control (IAM)" in left menu
   - Click "+ Add" → "Add role assignment"
   - **Role**: Select "Reader"
   - **Assign access to**: User, group, or service principal
   - **Select**: Search for `SandraEstok@FredesaLLC.onmicrosoft.com`
   - Click "Save"

4. **Verify** (wait 5-10 minutes for propagation)
   ```bash
   az resource list --resource-group fredesa-rg
   ```

---

### **Option 2: Azure CLI** (If you have Owner role)

```bash
# Assign Reader role to Sandra's account
az role assignment create \
  --assignee SandraEstok@FredesaLLC.onmicrosoft.com \
  --role "Reader" \
  --scope "/subscriptions/c99bdba1-68a6-4dde-afa8-2f437ba8dd22/resourceGroups/fredesa-rg"

# Verify assignment
az role assignment list \
  --assignee SandraEstok@FredesaLLC.onmicrosoft.com \
  --resource-group fredesa-rg \
  --output table
```

---

### **Option 3: PowerShell** (Windows/Azure Cloud Shell)

```powershell
# Assign Reader role
New-AzRoleAssignment `
  -SignInName "SandraEstok@FredesaLLC.onmicrosoft.com" `
  -RoleDefinitionName "Reader" `
  -ResourceGroupName "fredesa-rg"

# Verify assignment
Get-AzRoleAssignment `
  -SignInName "SandraEstok@FredesaLLC.onmicrosoft.com" `
  -ResourceGroupName "fredesa-rg"
```

---

## 🔍 Required Permissions

### **Minimum Recommended**:
```
Role: Reader
Scope: Resource Group (fredesa-rg)
Actions Enabled:
  ✅ View all resources
  ✅ Read resource properties
  ✅ List resources
  ❌ Cannot modify resources
  ❌ Cannot delete resources
  ❌ Cannot create resources
```

### **If Deployment is Needed**:
```
Role: Contributor
Scope: Resource Group (fredesa-rg)
Actions Enabled:
  ✅ All Reader permissions
  ✅ Create resources
  ✅ Modify resources
  ✅ Delete resources
  ❌ Cannot manage access permissions
```

---

## ✅ Verification Commands

Once permissions are assigned, verify with these commands:

```bash
# 1. List all resources in the resource group
az resource list --resource-group fredesa-rg --output table

# 2. Check PostgreSQL servers
az postgres flexible-server list --resource-group fredesa-rg --output table

# 3. Check Container Apps
az containerapp list --resource-group fredesa-rg --output table

# 4. Check Storage Accounts
az storage account list --resource-group fredesa-rg --output table

# 5. Check Redis Cache
az redis list --resource-group fredesa-rg --output table
```

---

## 🎯 After Permissions Are Fixed

### **Immediate Actions**:

1. **Verify Test Environment Status**
   ```bash
   # Check if test database exists
   az postgres flexible-server show \
     --name fredesa-db-test \
     --resource-group fredesa-rg

   # Check if test container app exists
   az containerapp show \
     --name fredesa-mcp-server-test \
     --resource-group fredesa-rg
   ```

2. **If Test Resources Don't Exist, Deploy Them**
   ```bash
   cd /Users/W2P/fredesa-ai-platform/scripts/deployment
   python3 setup_test_environment.py
   ```

3. **Update Verification Report**
   ```bash
   # Re-run verification with full access
   az resource list --resource-group fredesa-rg --query "[?contains(name, 'test')]" -o table
   ```

---

## 📊 Current Known Status

### **What We Can Verify Now** (without Reader role):
- ✅ Production API: HTTP 200 (via curl)
- ✅ Azure CLI installed and authenticated
- ✅ GitHub connection working
- ✅ All configuration files exist

### **What We Cannot Verify** (needs Reader role):
- ❓ Whether test database exists
- ❓ Whether test container app exists
- ❓ Resource states (running/stopped)
- ❓ Resource configurations
- ❓ Cost estimates

---

## 🔒 Security Notes

### **Best Practices**:
1. ✅ **Principle of Least Privilege**: Start with Reader role
2. ✅ **Resource Group Scope**: Don't grant subscription-wide access
3. ✅ **Review Periodically**: Audit role assignments quarterly
4. ✅ **Document Access**: Keep record of who has what access

### **Role Comparison**:
| Role | View Resources | Create Resources | Delete Resources | Manage Access |
|------|----------------|------------------|------------------|---------------|
| Reader | ✅ | ❌ | ❌ | ❌ |
| Contributor | ✅ | ✅ | ✅ | ❌ |
| Owner | ✅ | ✅ | ✅ | ✅ |

---

## 📞 Who to Contact

### **FreDeSa LLC Azure Administrators**:
Reach out to someone with **Owner** or **User Access Administrator** role on:
- Subscription: MCPP Subscription
- Resource Group: fredesa-rg

### **Typical Azure Administrators**:
- IT Department lead
- Cloud infrastructure team
- DevOps team lead
- Subscription owner

---

## 🎯 Quick Commands for Administrator

**For the person who will fix this, here's a quick copy-paste**:

```bash
# Azure Portal: https://portal.azure.com
# Go to: Resource Groups → fredesa-rg → Access control (IAM)
# Add role assignment: Reader → SandraEstok@FredesaLLC.onmicrosoft.com

# Or via CLI:
az role assignment create \
  --assignee SandraEstok@FredesaLLC.onmicrosoft.com \
  --role "Reader" \
  --scope "/subscriptions/c99bdba1-68a6-4dde-afa8-2f437ba8dd22/resourceGroups/fredesa-rg"

# Verify:
az role assignment list \
  --assignee SandraEstok@FredesaLLC.onmicrosoft.com \
  --resource-group fredesa-rg \
  --output table
```

---

## 📚 Additional Resources

- **Azure RBAC Documentation**: https://docs.microsoft.com/azure/role-based-access-control/
- **Built-in Roles**: https://docs.microsoft.com/azure/role-based-access-control/built-in-roles
- **Troubleshooting Access**: https://docs.microsoft.com/azure/role-based-access-control/troubleshooting

---

**Created**: January 3, 2026  
**Status**: Awaiting Owner/Administrator action  
**Expected Resolution Time**: 5-10 minutes after role assignment  
**Next Step**: Share this document with Azure administrator
