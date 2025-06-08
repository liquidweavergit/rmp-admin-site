import React from "react";
import { render, screen } from "@testing-library/react";
import { Provider } from "react-redux";
import { BrowserRouter } from "react-router-dom";
import { configureStore } from "@reduxjs/toolkit";
import ProtectedRoute from "../../../components/auth/ProtectedRoute";

// Mock the permissions utilities
jest.mock("../../../utils/permissions", () => ({
  hasPermission: jest.fn(),
  hasAnyPermission: jest.fn(),
  hasRole: jest.fn(),
  hasAnyRole: jest.fn(),
  hasMinimumRoleLevel: jest.fn(),
  ROLE_HIERARCHY: {
    Member: 10,
    Facilitator: 20,
    PTM: 30,
    Manager: 40,
    Director: 50,
    Admin: 60,
  },
}));

const mockPermissions = require("../../../utils/permissions");

// Mock the store hook
const mockUseGetUserProfileQuery = jest.fn();
jest.mock("../../../store", () => ({
  useGetUserProfileQuery: () => mockUseGetUserProfileQuery(),
  RootState: {},
}));

// Mock useSelector
const mockUseSelector = jest.fn();
jest.mock("react-redux", () => ({
  ...jest.requireActual("react-redux"),
  useSelector: () => mockUseSelector(),
}));

const createMockStore = () => {
  return configureStore({
    reducer: {
      auth: (state = {}) => state,
    },
  });
};

const renderWithProviders = (component: React.ReactElement) => {
  const store = createMockStore();
  return render(
    <Provider store={store}>
      <BrowserRouter>{component}</BrowserRouter>
    </Provider>,
  );
};

const mockUserProfile = {
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
  roles: [
    {
      role: {
        id: 1,
        name: "Member",
        description: "Basic member",
        priority: 10,
        permissions: [],
      },
      is_primary: true,
      assigned_at: "2024-01-01T00:00:00Z",
    },
  ],
  permissions: ["circles:view", "events:view"],
};

describe("ProtectedRoute - Core Functionality", () => {
  const TestComponent = () => <div>Protected Content</div>;

  beforeEach(() => {
    jest.clearAllMocks();
    mockUseSelector.mockReturnValue({
      isAuthenticated: true,
      token: "valid-token",
    });
    mockUseGetUserProfileQuery.mockReturnValue({
      data: mockUserProfile,
      isLoading: false,
      error: null,
      isError: false,
    });
  });

  describe("Basic Authentication", () => {
    it("should render protected content when user is authenticated", () => {
      renderWithProviders(
        <ProtectedRoute>
          <TestComponent />
        </ProtectedRoute>,
      );

      expect(screen.getByText("Protected Content")).toBeInTheDocument();
    });

    it("should show loading state when profile is loading", () => {
      mockUseGetUserProfileQuery.mockReturnValue({
        data: null,
        isLoading: true,
        error: null,
        isError: false,
      });

      renderWithProviders(
        <ProtectedRoute>
          <TestComponent />
        </ProtectedRoute>,
      );

      expect(screen.getByText("Loading user permissions...")).toBeInTheDocument();
      expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
    });

    it("should not render when user is not authenticated", () => {
      mockUseSelector.mockReturnValue({
        isAuthenticated: false,
        token: null,
      });

      renderWithProviders(
        <ProtectedRoute>
          <TestComponent />
        </ProtectedRoute>,
      );

      expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
    });
  });

  describe("Permission-based Access", () => {
    it("should allow access when user has required permission", () => {
      mockPermissions.hasPermission.mockReturnValue(true);

      renderWithProviders(
        <ProtectedRoute requiredPermission="circles:view">
          <TestComponent />
        </ProtectedRoute>,
      );

      expect(screen.getByText("Protected Content")).toBeInTheDocument();
      expect(mockPermissions.hasPermission).toHaveBeenCalledWith(mockUserProfile, "circles:view");
    });

    it("should deny access when user lacks required permission", () => {
      mockPermissions.hasPermission.mockReturnValue(false);

      renderWithProviders(
        <ProtectedRoute requiredPermission="admin:manage" showUnauthorizedMessage={true}>
          <TestComponent />
        </ProtectedRoute>,
      );

      expect(screen.getByText("Access Denied")).toBeInTheDocument();
      expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
    });

    it("should handle multiple permissions with ANY logic", () => {
      mockPermissions.hasAnyPermission.mockReturnValue(true);

      renderWithProviders(
        <ProtectedRoute
          requiredPermissions={["circles:view", "events:view"]}
          requireAllPermissions={false}
        >
          <TestComponent />
        </ProtectedRoute>,
      );

      expect(screen.getByText("Protected Content")).toBeInTheDocument();
      expect(mockPermissions.hasAnyPermission).toHaveBeenCalledWith(mockUserProfile, [
        "circles:view",
        "events:view",
      ]);
    });
  });

  describe("Role-based Access", () => {
    it("should allow access when user has required role", () => {
      mockPermissions.hasRole.mockReturnValue(true);

      renderWithProviders(
        <ProtectedRoute requiredRole="Member">
          <TestComponent />
        </ProtectedRoute>,
      );

      expect(screen.getByText("Protected Content")).toBeInTheDocument();
      expect(mockPermissions.hasRole).toHaveBeenCalledWith(mockUserProfile, "Member");
    });

    it("should deny access when user lacks required role", () => {
      mockPermissions.hasRole.mockReturnValue(false);

      renderWithProviders(
        <ProtectedRoute requiredRole="Admin" showUnauthorizedMessage={true}>
          <TestComponent />
        </ProtectedRoute>,
      );

      expect(screen.getByText("Access Denied")).toBeInTheDocument();
      expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
    });

    it("should handle multiple roles", () => {
      mockPermissions.hasAnyRole.mockReturnValue(true);

      renderWithProviders(
        <ProtectedRoute requiredRoles={["Member", "Facilitator"]} requireAllRoles={false}>
          <TestComponent />
        </ProtectedRoute>,
      );

      expect(screen.getByText("Protected Content")).toBeInTheDocument();
      expect(mockPermissions.hasAnyRole).toHaveBeenCalledWith(mockUserProfile, [
        "Member",
        "Facilitator",
      ]);
    });
  });

  describe("Minimum Role Level", () => {
    it("should allow access when user meets minimum role level", () => {
      mockPermissions.hasMinimumRoleLevel.mockReturnValue(true);

      renderWithProviders(
        <ProtectedRoute minimumRole="Member">
          <TestComponent />
        </ProtectedRoute>,
      );

      expect(screen.getByText("Protected Content")).toBeInTheDocument();
      expect(mockPermissions.hasMinimumRoleLevel).toHaveBeenCalledWith(mockUserProfile, "Member");
    });

    it("should deny access when user does not meet minimum role level", () => {
      mockPermissions.hasMinimumRoleLevel.mockReturnValue(false);

      renderWithProviders(
        <ProtectedRoute minimumRole="Admin" showUnauthorizedMessage={true}>
          <TestComponent />
        </ProtectedRoute>,
      );

      expect(screen.getByText("Access Denied")).toBeInTheDocument();
      expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
    });
  });

  describe("Custom Permission Check", () => {
    it("should allow access when custom check returns true", () => {
      const customCheck = jest.fn().mockReturnValue(true);

      renderWithProviders(
        <ProtectedRoute customPermissionCheck={customCheck}>
          <TestComponent />
        </ProtectedRoute>,
      );

      expect(screen.getByText("Protected Content")).toBeInTheDocument();
      expect(customCheck).toHaveBeenCalledWith(mockUserProfile);
    });

    it("should deny access when custom check returns false", () => {
      const customCheck = jest.fn().mockReturnValue(false);

      renderWithProviders(
        <ProtectedRoute customPermissionCheck={customCheck} showUnauthorizedMessage={true}>
          <TestComponent />
        </ProtectedRoute>,
      );

      expect(screen.getByText("Access Denied")).toBeInTheDocument();
      expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
      expect(customCheck).toHaveBeenCalledWith(mockUserProfile);
    });
  });

  describe("Error Handling", () => {
    it("should render custom fallback during loading", () => {
      mockUseGetUserProfileQuery.mockReturnValue({
        data: null,
        isLoading: true,
        error: null,
        isError: false,
      });

      const CustomFallback = () => <div>Custom Loading...</div>;

      renderWithProviders(
        <ProtectedRoute fallback={<CustomFallback />}>
          <TestComponent />
        </ProtectedRoute>,
      );

      expect(screen.getByText("Custom Loading...")).toBeInTheDocument();
    });

    it("should show user roles in unauthorized message", () => {
      mockPermissions.hasRole.mockReturnValue(false);

      renderWithProviders(
        <ProtectedRoute requiredRole="Admin" showUnauthorizedMessage={true}>
          <TestComponent />
        </ProtectedRoute>,
      );

      expect(screen.getByText("Access Denied")).toBeInTheDocument();
      expect(screen.getByText(/Your current role: Member/)).toBeInTheDocument();
    });
  });
});
