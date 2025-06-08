import {
  hasPermission,
  hasAnyPermission,
  hasAllPermissions,
  hasRole,
  hasAnyRole,
  getPrimaryRole,
  getHighestPriorityRole,
  canAccessResource,
  hasMinimumRoleLevel,
  canManageCircles,
  canManageEvents,
  canManageUsers,
  isSystemAdmin,
  ROLE_HIERARCHY,
  PERMISSION_GROUPS,
} from "../../utils/permissions";
import type { UserProfileResponse, RoleResponse, UserRoleResponse } from "../../store";

// Mock user profile data for testing
const mockPermissions = [
  { id: 1, name: "circles:view", description: "View circles", resource: "circles", action: "view" },
  {
    id: 2,
    name: "circles:create",
    description: "Create circles",
    resource: "circles",
    action: "create",
  },
  { id: 3, name: "events:view", description: "View events", resource: "events", action: "view" },
  { id: 4, name: "users:manage", description: "Manage users", resource: "users", action: "manage" },
  { id: 5, name: "system:admin", description: "System admin", resource: "system", action: "admin" },
];

const mockMemberRole: RoleResponse = {
  id: 1,
  name: "Member",
  description: "Basic member",
  priority: 10,
  permissions: [mockPermissions[0], mockPermissions[2]], // circles:view, events:view
};

const mockFacilitatorRole: RoleResponse = {
  id: 2,
  name: "Facilitator",
  description: "Circle facilitator",
  priority: 20,
  permissions: [mockPermissions[0], mockPermissions[1], mockPermissions[2]], // circles:view, circles:create, events:view
};

const mockAdminRole: RoleResponse = {
  id: 3,
  name: "Admin",
  description: "System administrator",
  priority: 60,
  permissions: mockPermissions, // All permissions
};

const createMockUserProfile = (
  roles: UserRoleResponse[],
  permissions: string[],
): UserProfileResponse => ({
  id: 1,
  email: "test@example.com",
  first_name: "Test",
  last_name: "User",
  phone: "+1234567890",
  is_active: true,
  is_verified: true,
  email_verified: true,
  phone_verified: true,
  created_at: "2024-01-01T00:00:00Z",
  roles,
  permissions,
});

describe("Permission Utilities", () => {
  describe("hasPermission", () => {
    it("should return true when user has the permission", () => {
      const userProfile = createMockUserProfile([], ["circles:view", "events:view"]);
      expect(hasPermission(userProfile, "circles:view")).toBe(true);
    });

    it("should return false when user does not have the permission", () => {
      const userProfile = createMockUserProfile([], ["circles:view"]);
      expect(hasPermission(userProfile, "users:manage")).toBe(false);
    });

    it("should return false when userProfile is null", () => {
      expect(hasPermission(null, "circles:view")).toBe(false);
    });

    it("should return false when permissions array is empty", () => {
      const userProfile = createMockUserProfile([], []);
      expect(hasPermission(userProfile, "circles:view")).toBe(false);
    });
  });

  describe("hasAnyPermission", () => {
    it("should return true when user has at least one permission", () => {
      const userProfile = createMockUserProfile([], ["circles:view", "events:view"]);
      expect(hasAnyPermission(userProfile, ["circles:view", "users:manage"])).toBe(true);
    });

    it("should return false when user has none of the permissions", () => {
      const userProfile = createMockUserProfile([], ["circles:view"]);
      expect(hasAnyPermission(userProfile, ["users:manage", "system:admin"])).toBe(false);
    });

    it("should return false when permissions array is empty", () => {
      const userProfile = createMockUserProfile([], ["circles:view"]);
      expect(hasAnyPermission(userProfile, [])).toBe(false);
    });
  });

  describe("hasAllPermissions", () => {
    it("should return true when user has all permissions", () => {
      const userProfile = createMockUserProfile(
        [],
        ["circles:view", "events:view", "users:manage"],
      );
      expect(hasAllPermissions(userProfile, ["circles:view", "events:view"])).toBe(true);
    });

    it("should return false when user is missing some permissions", () => {
      const userProfile = createMockUserProfile([], ["circles:view"]);
      expect(hasAllPermissions(userProfile, ["circles:view", "users:manage"])).toBe(false);
    });
  });

  describe("hasRole", () => {
    it("should return true when user has the role", () => {
      const userRoles: UserRoleResponse[] = [
        {
          role: mockMemberRole,
          is_primary: true,
          assigned_at: "2024-01-01T00:00:00Z",
        },
      ];
      const userProfile = createMockUserProfile(userRoles, []);
      expect(hasRole(userProfile, "Member")).toBe(true);
    });

    it("should return false when user does not have the role", () => {
      const userRoles: UserRoleResponse[] = [
        {
          role: mockMemberRole,
          is_primary: true,
          assigned_at: "2024-01-01T00:00:00Z",
        },
      ];
      const userProfile = createMockUserProfile(userRoles, []);
      expect(hasRole(userProfile, "Admin")).toBe(false);
    });

    it("should return false when userProfile is null", () => {
      expect(hasRole(null, "Member")).toBe(false);
    });
  });

  describe("hasAnyRole", () => {
    it("should return true when user has at least one role", () => {
      const userRoles: UserRoleResponse[] = [
        {
          role: mockMemberRole,
          is_primary: true,
          assigned_at: "2024-01-01T00:00:00Z",
        },
      ];
      const userProfile = createMockUserProfile(userRoles, []);
      expect(hasAnyRole(userProfile, ["Member", "Admin"])).toBe(true);
    });

    it("should return false when user has none of the roles", () => {
      const userRoles: UserRoleResponse[] = [
        {
          role: mockMemberRole,
          is_primary: true,
          assigned_at: "2024-01-01T00:00:00Z",
        },
      ];
      const userProfile = createMockUserProfile(userRoles, []);
      expect(hasAnyRole(userProfile, ["Admin", "Director"])).toBe(false);
    });
  });

  describe("getPrimaryRole", () => {
    it("should return the primary role", () => {
      const userRoles: UserRoleResponse[] = [
        {
          role: mockMemberRole,
          is_primary: false,
          assigned_at: "2024-01-01T00:00:00Z",
        },
        {
          role: mockFacilitatorRole,
          is_primary: true,
          assigned_at: "2024-01-01T00:00:00Z",
        },
      ];
      const userProfile = createMockUserProfile(userRoles, []);
      const primaryRole = getPrimaryRole(userProfile);
      expect(primaryRole?.name).toBe("Facilitator");
    });

    it("should return null when no primary role is set", () => {
      const userRoles: UserRoleResponse[] = [
        {
          role: mockMemberRole,
          is_primary: false,
          assigned_at: "2024-01-01T00:00:00Z",
        },
      ];
      const userProfile = createMockUserProfile(userRoles, []);
      expect(getPrimaryRole(userProfile)).toBeNull();
    });

    it("should return null when userProfile is null", () => {
      expect(getPrimaryRole(null)).toBeNull();
    });
  });

  describe("getHighestPriorityRole", () => {
    it("should return the role with highest priority", () => {
      const userRoles: UserRoleResponse[] = [
        {
          role: mockMemberRole, // priority 10
          is_primary: true,
          assigned_at: "2024-01-01T00:00:00Z",
        },
        {
          role: mockAdminRole, // priority 60
          is_primary: false,
          assigned_at: "2024-01-01T00:00:00Z",
        },
      ];
      const userProfile = createMockUserProfile(userRoles, []);
      const highestRole = getHighestPriorityRole(userProfile);
      expect(highestRole?.name).toBe("Admin");
    });

    it("should return null when user has no roles", () => {
      const userProfile = createMockUserProfile([], []);
      expect(getHighestPriorityRole(userProfile)).toBeNull();
    });
  });

  describe("canAccessResource", () => {
    it("should return true when user can access resource with action", () => {
      const userProfile = createMockUserProfile([], ["circles:view", "events:create"]);
      expect(canAccessResource(userProfile, "circles", "view")).toBe(true);
      expect(canAccessResource(userProfile, "events", "create")).toBe(true);
    });

    it("should return false when user cannot access resource with action", () => {
      const userProfile = createMockUserProfile([], ["circles:view"]);
      expect(canAccessResource(userProfile, "circles", "create")).toBe(false);
      expect(canAccessResource(userProfile, "users", "manage")).toBe(false);
    });
  });

  describe("hasMinimumRoleLevel", () => {
    it("should return true when user has minimum role level", () => {
      const userRoles: UserRoleResponse[] = [
        {
          role: mockAdminRole, // priority 60
          is_primary: true,
          assigned_at: "2024-01-01T00:00:00Z",
        },
      ];
      const userProfile = createMockUserProfile(userRoles, []);
      expect(hasMinimumRoleLevel(userProfile, "Member")).toBe(true); // 60 >= 10
      expect(hasMinimumRoleLevel(userProfile, "Facilitator")).toBe(true); // 60 >= 20
    });

    it("should return false when user does not have minimum role level", () => {
      const userRoles: UserRoleResponse[] = [
        {
          role: mockMemberRole, // priority 10
          is_primary: true,
          assigned_at: "2024-01-01T00:00:00Z",
        },
      ];
      const userProfile = createMockUserProfile(userRoles, []);
      expect(hasMinimumRoleLevel(userProfile, "Admin")).toBe(false); // 10 < 60
    });
  });

  describe("Permission Group Functions", () => {
    describe("canManageCircles", () => {
      it("should return true when user has circle management permissions", () => {
        const userProfile = createMockUserProfile([], ["circles:create", "circles:manage"]);
        expect(canManageCircles(userProfile)).toBe(true);
      });

      it("should return false when user has no circle management permissions", () => {
        const userProfile = createMockUserProfile([], ["events:view"]);
        expect(canManageCircles(userProfile)).toBe(false);
      });
    });

    describe("canManageEvents", () => {
      it("should return true when user has event management permissions", () => {
        const userProfile = createMockUserProfile([], ["events:create", "events:manage"]);
        expect(canManageEvents(userProfile)).toBe(true);
      });

      it("should return false when user has no event management permissions", () => {
        const userProfile = createMockUserProfile([], ["circles:view"]);
        expect(canManageEvents(userProfile)).toBe(false);
      });
    });

    describe("canManageUsers", () => {
      it("should return true when user has user management permissions", () => {
        const userProfile = createMockUserProfile([], ["users:create", "users:manage"]);
        expect(canManageUsers(userProfile)).toBe(true);
      });

      it("should return false when user has no user management permissions", () => {
        const userProfile = createMockUserProfile([], ["circles:view"]);
        expect(canManageUsers(userProfile)).toBe(false);
      });
    });

    describe("isSystemAdmin", () => {
      it("should return true when user has system admin permissions", () => {
        const userProfile = createMockUserProfile([], ["system:admin", "system:configure"]);
        expect(isSystemAdmin(userProfile)).toBe(true);
      });

      it("should return false when user has no system admin permissions", () => {
        const userProfile = createMockUserProfile([], ["circles:view"]);
        expect(isSystemAdmin(userProfile)).toBe(false);
      });
    });
  });

  describe("Constants", () => {
    it("should have correct role hierarchy values", () => {
      expect(ROLE_HIERARCHY.Member).toBe(10);
      expect(ROLE_HIERARCHY.Facilitator).toBe(20);
      expect(ROLE_HIERARCHY.PTM).toBe(30);
      expect(ROLE_HIERARCHY.Manager).toBe(40);
      expect(ROLE_HIERARCHY.Director).toBe(50);
      expect(ROLE_HIERARCHY.Admin).toBe(60);
    });

    it("should have correct permission groups", () => {
      expect(PERMISSION_GROUPS.CIRCLE_MANAGEMENT).toContain("circles:create");
      expect(PERMISSION_GROUPS.EVENT_MANAGEMENT).toContain("events:create");
      expect(PERMISSION_GROUPS.USER_MANAGEMENT).toContain("users:manage");
      expect(PERMISSION_GROUPS.SYSTEM_ADMIN).toContain("system:admin");
    });
  });
});
