/**
 * Permission utility functions for role-based access control
 */

import type { UserProfileResponse, RoleResponse, UserRoleResponse } from "../store";

/**
 * Check if user has a specific permission
 */
export const hasPermission = (
  userProfile: UserProfileResponse | null,
  permission: string,
): boolean => {
  if (!userProfile || !userProfile.permissions) {
    return false;
  }
  return userProfile.permissions.includes(permission);
};

/**
 * Check if user has any of the specified permissions
 */
export const hasAnyPermission = (
  userProfile: UserProfileResponse | null,
  permissions: string[],
): boolean => {
  if (!userProfile || !userProfile.permissions) {
    return false;
  }
  return permissions.some((permission) => userProfile.permissions.includes(permission));
};

/**
 * Check if user has all of the specified permissions
 */
export const hasAllPermissions = (
  userProfile: UserProfileResponse | null,
  permissions: string[],
): boolean => {
  if (!userProfile || !userProfile.permissions) {
    return false;
  }
  return permissions.every((permission) => userProfile.permissions.includes(permission));
};

/**
 * Check if user has a specific role
 */
export const hasRole = (userProfile: UserProfileResponse | null, roleName: string): boolean => {
  if (!userProfile || !userProfile.roles) {
    return false;
  }
  return userProfile.roles.some((userRole) => userRole.role.name === roleName);
};

/**
 * Check if user has any of the specified roles
 */
export const hasAnyRole = (
  userProfile: UserProfileResponse | null,
  roleNames: string[],
): boolean => {
  if (!userProfile || !userProfile.roles) {
    return false;
  }
  return roleNames.some((roleName) =>
    userProfile.roles.some((userRole) => userRole.role.name === roleName),
  );
};

/**
 * Get user's primary role
 */
export const getPrimaryRole = (userProfile: UserProfileResponse | null): RoleResponse | null => {
  if (!userProfile || !userProfile.roles) {
    return null;
  }
  const primaryUserRole = userProfile.roles.find((userRole) => userRole.is_primary);
  return primaryUserRole ? primaryUserRole.role : null;
};

/**
 * Get user's highest priority role
 */
export const getHighestPriorityRole = (
  userProfile: UserProfileResponse | null,
): RoleResponse | null => {
  if (!userProfile || !userProfile.roles || userProfile.roles.length === 0) {
    return null;
  }

  return userProfile.roles.reduce((highest, userRole) => {
    if (!highest || userRole.role.priority > highest.role.priority) {
      return userRole;
    }
    return highest;
  }).role;
};

/**
 * Check if user can access a resource based on permissions
 */
export const canAccessResource = (
  userProfile: UserProfileResponse | null,
  resource: string,
  action: string,
): boolean => {
  const permission = `${resource}:${action}`;
  return hasPermission(userProfile, permission);
};

/**
 * Role hierarchy levels for easy comparison
 */
export const ROLE_HIERARCHY = {
  Member: 10,
  Facilitator: 20,
  PTM: 30,
  Manager: 40,
  Director: 50,
  Admin: 60,
};

/**
 * Check if user has minimum role level
 */
export const hasMinimumRoleLevel = (
  userProfile: UserProfileResponse | null,
  minimumRole: keyof typeof ROLE_HIERARCHY,
): boolean => {
  if (!userProfile || !userProfile.roles) {
    return false;
  }

  const userHighestRole = getHighestPriorityRole(userProfile);
  if (!userHighestRole) {
    return false;
  }

  const userLevel = ROLE_HIERARCHY[userHighestRole.name as keyof typeof ROLE_HIERARCHY] || 0;
  const minimumLevel = ROLE_HIERARCHY[minimumRole];

  return userLevel >= minimumLevel;
};

/**
 * Common permission groups for easy checking
 */
export const PERMISSION_GROUPS = {
  CIRCLE_MANAGEMENT: [
    "circles:create",
    "circles:manage",
    "circles:add_members",
    "circles:remove_members",
    "circles:edit",
  ],
  EVENT_MANAGEMENT: ["events:create", "events:manage", "events:staff_assign", "events:logistics"],
  USER_MANAGEMENT: ["users:create", "users:manage", "users:delete", "users:roles_assign"],
  SYSTEM_ADMIN: ["system:admin", "system:configure", "system:maintain"],
};

/**
 * Check if user can manage circles
 */
export const canManageCircles = (userProfile: UserProfileResponse | null): boolean => {
  return hasAnyPermission(userProfile, PERMISSION_GROUPS.CIRCLE_MANAGEMENT);
};

/**
 * Check if user can manage events
 */
export const canManageEvents = (userProfile: UserProfileResponse | null): boolean => {
  return hasAnyPermission(userProfile, PERMISSION_GROUPS.EVENT_MANAGEMENT);
};

/**
 * Check if user can manage users
 */
export const canManageUsers = (userProfile: UserProfileResponse | null): boolean => {
  return hasAnyPermission(userProfile, PERMISSION_GROUPS.USER_MANAGEMENT);
};

/**
 * Check if user is system admin
 */
export const isSystemAdmin = (userProfile: UserProfileResponse | null): boolean => {
  return hasAnyPermission(userProfile, PERMISSION_GROUPS.SYSTEM_ADMIN);
};
