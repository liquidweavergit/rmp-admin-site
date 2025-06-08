import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { Box, CircularProgress, Alert, Typography } from "@mui/material";
import { useSelector } from "react-redux";
import { RootState, useGetUserProfileQuery } from "../../store";
import {
  hasPermission,
  hasAnyPermission,
  hasRole,
  hasAnyRole,
  hasMinimumRoleLevel,
  ROLE_HIERARCHY,
} from "../../utils/permissions";

interface ProtectedRouteProps {
  children: React.ReactNode;

  // Permission-based access control
  requiredPermission?: string;
  requiredPermissions?: string[];
  requireAllPermissions?: boolean; // If true, user must have ALL permissions, otherwise ANY

  // Role-based access control
  requiredRole?: string;
  requiredRoles?: string[];
  requireAllRoles?: boolean; // If true, user must have ALL roles, otherwise ANY

  // Minimum role level (uses hierarchy)
  minimumRole?: keyof typeof ROLE_HIERARCHY;

  // Custom permission check function
  customPermissionCheck?: (userProfile: any) => boolean;

  // Redirect options
  redirectTo?: string;
  showUnauthorizedMessage?: boolean;

  // Loading and error handling
  fallback?: React.ReactNode;
}

/**
 * ProtectedRoute component that enforces role-based access control
 *
 * Features:
 * - Permission-based access (single or multiple permissions)
 * - Role-based access (single or multiple roles)
 * - Minimum role level checking using hierarchy
 * - Custom permission checking function
 * - Configurable redirects and error messages
 * - Loading states while fetching user profile
 */
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredPermission,
  requiredPermissions,
  requireAllPermissions = false,
  requiredRole,
  requiredRoles,
  requireAllRoles = false,
  minimumRole,
  customPermissionCheck,
  redirectTo = "/login",
  showUnauthorizedMessage = true,
  fallback,
}) => {
  const location = useLocation();
  const { isAuthenticated, token } = useSelector((state: RootState) => state.auth);

  // Fetch user profile with roles and permissions
  const {
    data: userProfile,
    isLoading,
    error,
    isError,
  } = useGetUserProfileQuery(undefined, {
    skip: !isAuthenticated || !token,
  });

  // Show loading state while fetching user profile
  if (isLoading) {
    return (
      fallback || (
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          minHeight="200px"
          flexDirection="column"
          gap={2}
        >
          <CircularProgress />
          <Typography variant="body2" color="text.secondary">
            Loading user permissions...
          </Typography>
        </Box>
      )
    );
  }

  // Handle authentication errors
  if (isError || error) {
    console.error("Error fetching user profile:", error);
    return <Navigate to={redirectTo} state={{ from: location }} replace />;
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated || !token) {
    return <Navigate to={redirectTo} state={{ from: location }} replace />;
  }

  // If no user profile data, redirect to login
  if (!userProfile) {
    return <Navigate to={redirectTo} state={{ from: location }} replace />;
  }

  // Check permissions
  let hasRequiredPermissions = true;

  // Single permission check
  if (requiredPermission) {
    hasRequiredPermissions = hasPermission(userProfile, requiredPermission);
  }

  // Multiple permissions check
  if (requiredPermissions && requiredPermissions.length > 0) {
    if (requireAllPermissions) {
      hasRequiredPermissions = requiredPermissions.every((permission) =>
        hasPermission(userProfile, permission),
      );
    } else {
      hasRequiredPermissions = hasAnyPermission(userProfile, requiredPermissions);
    }
  }

  // Check roles
  let hasRequiredRoles = true;

  // Single role check
  if (requiredRole) {
    hasRequiredRoles = hasRole(userProfile, requiredRole);
  }

  // Multiple roles check
  if (requiredRoles && requiredRoles.length > 0) {
    if (requireAllRoles) {
      hasRequiredRoles = requiredRoles.every((role) => hasRole(userProfile, role));
    } else {
      hasRequiredRoles = hasAnyRole(userProfile, requiredRoles);
    }
  }

  // Minimum role level check
  let hasMinimumRoleAccess = true;
  if (minimumRole) {
    hasMinimumRoleAccess = hasMinimumRoleLevel(userProfile, minimumRole);
  }

  // Custom permission check
  let hasCustomPermission = true;
  if (customPermissionCheck) {
    hasCustomPermission = customPermissionCheck(userProfile);
  }

  // Combine all checks
  const hasAccess =
    hasRequiredPermissions && hasRequiredRoles && hasMinimumRoleAccess && hasCustomPermission;

  // If user doesn't have access, show unauthorized message or redirect
  if (!hasAccess) {
    if (showUnauthorizedMessage) {
      return (
        <Box p={3}>
          <Alert severity="error">
            <Typography variant="h6" gutterBottom>
              Access Denied
            </Typography>
            <Typography variant="body2">
              You don't have the required permissions to access this page.
            </Typography>
            {userProfile.roles.length > 0 && (
              <Typography variant="body2" sx={{ mt: 1 }}>
                Your current role{userProfile.roles.length > 1 ? "s" : ""}:{" "}
                {userProfile.roles.map((ur) => ur.role.name).join(", ")}
              </Typography>
            )}
          </Alert>
        </Box>
      );
    } else {
      return <Navigate to={redirectTo} state={{ from: location }} replace />;
    }
  }

  // User has access, render the protected content
  return <>{children}</>;
};

export default ProtectedRoute;
