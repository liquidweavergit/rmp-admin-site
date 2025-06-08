import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { Provider } from "react-redux";
import { BrowserRouter } from "react-router-dom";
import { configureStore } from "@reduxjs/toolkit";
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import ProtectedRoute from "../../../components/auth/ProtectedRoute";
import type { UserProfileResponse } from "../../../store";

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

// Create a mock API slice for testing
const mockApi = createApi({
  reducerPath: "mockApi",
  baseQuery: fetchBaseQuery({ baseUrl: "/" }),
  endpoints: (builder) => ({
    getUserProfile: builder.query<UserProfileResponse, void>({
      query: () => "/profile",
    }),
  }),
});

// Mock auth slice
const mockAuthSlice = {
  name: "auth",
  initialState: {
    token: null,
    refreshToken: null,
    user: null,
    userProfile: null,
    isAuthenticated: false,
  },
  reducers: {},
};

const createMockStore = (authState: any, profileData?: UserProfileResponse, profileError?: any) => {
  return configureStore({
    reducer: {
      [mockApi.reducerPath]: mockApi.reducer,
      auth: (state = authState) => state,
    },
    middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(mockApi.middleware),
    preloadedState: {
      auth: authState,
      [mockApi.reducerPath]: {
        queries: {
          "getUserProfile(undefined)": profileData
            ? {
                status: "fulfilled",
                data: profileData,
                isLoading: false,
                isError: false,
              }
            : profileError
              ? {
                  status: "rejected",
                  error: profileError,
                  isLoading: false,
                  isError: true,
                }
              : {
                  status: "pending",
                  isLoading: true,
                  isError: false,
                },
        },
        mutations: {},
        provided: {},
        subscriptions: {},
        config: {
          online: true,
          focused: true,
          middlewareRegistered: true,
          refetchOnFocus: false,
          refetchOnReconnect: false,
          refetchOnMountOrArgChange: false,
          keepUnusedDataFor: 60,
          reducerPath: "mockApi",
        },
      },
    },
  });
};

const renderWithProviders = (
  component: React.ReactElement,
  authState: any,
  profileData?: UserProfileResponse,
  profileError?: any,
) => {
  const store = createMockStore(authState, profileData, profileError);
  return render(
    <Provider store={store}>
      <BrowserRouter>{component}</BrowserRouter>
    </Provider>,
  );
};

const mockUserProfile: UserProfileResponse = {
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

describe("ProtectedRoute", () => {
  const TestComponent = () => <div>Protected Content</div>;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("Authentication Checks", () => {
    it("should redirect to login when user is not authenticated", () => {
      const authState = {
        token: null,
        refreshToken: null,
        user: null,
        userProfile: null,
        isAuthenticated: false,
      };

      renderWithProviders(
        <ProtectedRoute>
          <TestComponent />
        </ProtectedRoute>,
        authState,
      );

      // Should not render protected content
      expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
    });

    it("should show loading state while fetching user profile", () => {
      const authState = {
        token: "valid-token",
        refreshToken: "valid-refresh-token",
        user: null,
        userProfile: null,
        isAuthenticated: true,
      };

      renderWithProviders(
        <ProtectedRoute>
          <TestComponent />
        </ProtectedRoute>,
        authState,
      );

      expect(screen.getByText("Loading user permissions...")).toBeInTheDocument();
    });

    it("should redirect to login on profile fetch error", () => {
      const authState = {
        token: "valid-token",
        refreshToken: "valid-refresh-token",
        user: null,
        userProfile: null,
        isAuthenticated: true,
      };

      const profileError = { status: 401, message: "Unauthorized" };

      renderWithProviders(
        <ProtectedRoute>
          <TestComponent />
        </ProtectedRoute>,
        authState,
        undefined,
        profileError,
      );

      // Should not render protected content
      expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
    });

    it("should render protected content when user is authenticated and has profile", async () => {
      const authState = {
        token: "valid-token",
        refreshToken: "valid-refresh-token",
        user: null,
        userProfile: null,
        isAuthenticated: true,
      };

      renderWithProviders(
        <ProtectedRoute>
          <TestComponent />
        </ProtectedRoute>,
        authState,
        mockUserProfile,
      );

      await waitFor(() => {
        expect(screen.getByText("Protected Content")).toBeInTheDocument();
      });
    });
  });

  describe("Permission-based Access Control", () => {
    const authState = {
      token: "valid-token",
      refreshToken: "valid-refresh-token",
      user: null,
      userProfile: null,
      isAuthenticated: true,
    };

    it("should allow access when user has required permission", async () => {
      const { hasPermission } = require("../../../utils/permissions");
      hasPermission.mockReturnValue(true);

      renderWithProviders(
        <ProtectedRoute requiredPermission="circles:view">
          <TestComponent />
        </ProtectedRoute>,
        authState,
        mockUserProfile,
      );

      await waitFor(() => {
        expect(screen.getByText("Protected Content")).toBeInTheDocument();
      });

      expect(hasPermission).toHaveBeenCalledWith(mockUserProfile, "circles:view");
    });

    it("should deny access when user lacks required permission", async () => {
      const { hasPermission } = require("../../../utils/permissions");
      hasPermission.mockReturnValue(false);

      renderWithProviders(
        <ProtectedRoute requiredPermission="admin:manage" showUnauthorizedMessage={true}>
          <TestComponent />
        </ProtectedRoute>,
        authState,
        mockUserProfile,
      );

      await waitFor(() => {
        expect(screen.getByText("Access Denied")).toBeInTheDocument();
        expect(screen.getByText(/You don't have the required permissions/)).toBeInTheDocument();
      });

      expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
    });

    it("should handle multiple required permissions with ANY logic", async () => {
      const { hasAnyPermission } = require("../../../utils/permissions");
      hasAnyPermission.mockReturnValue(true);

      renderWithProviders(
        <ProtectedRoute
          requiredPermissions={["circles:view", "events:view"]}
          requireAllPermissions={false}
        >
          <TestComponent />
        </ProtectedRoute>,
        authState,
        mockUserProfile,
      );

      await waitFor(() => {
        expect(screen.getByText("Protected Content")).toBeInTheDocument();
      });

      expect(hasAnyPermission).toHaveBeenCalledWith(mockUserProfile, [
        "circles:view",
        "events:view",
      ]);
    });

    it("should handle multiple required permissions with ALL logic", async () => {
      const { hasPermission } = require("../../../utils/permissions");
      hasPermission.mockImplementation((profile, permission) => {
        return ["circles:view", "events:view"].includes(permission);
      });

      renderWithProviders(
        <ProtectedRoute
          requiredPermissions={["circles:view", "events:view"]}
          requireAllPermissions={true}
        >
          <TestComponent />
        </ProtectedRoute>,
        authState,
        mockUserProfile,
      );

      await waitFor(() => {
        expect(screen.getByText("Protected Content")).toBeInTheDocument();
      });
    });
  });

  describe("Role-based Access Control", () => {
    const authState = {
      token: "valid-token",
      refreshToken: "valid-refresh-token",
      user: null,
      userProfile: null,
      isAuthenticated: true,
    };

    it("should allow access when user has required role", async () => {
      const { hasRole } = require("../../../utils/permissions");
      hasRole.mockReturnValue(true);

      renderWithProviders(
        <ProtectedRoute requiredRole="Member">
          <TestComponent />
        </ProtectedRoute>,
        authState,
        mockUserProfile,
      );

      await waitFor(() => {
        expect(screen.getByText("Protected Content")).toBeInTheDocument();
      });

      expect(hasRole).toHaveBeenCalledWith(mockUserProfile, "Member");
    });

    it("should deny access when user lacks required role", async () => {
      const { hasRole } = require("../../../utils/permissions");
      hasRole.mockReturnValue(false);

      renderWithProviders(
        <ProtectedRoute requiredRole="Admin" showUnauthorizedMessage={true}>
          <TestComponent />
        </ProtectedRoute>,
        authState,
        mockUserProfile,
      );

      await waitFor(() => {
        expect(screen.getByText("Access Denied")).toBeInTheDocument();
      });

      expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
    });

    it("should handle multiple required roles", async () => {
      const { hasAnyRole } = require("../../../utils/permissions");
      hasAnyRole.mockReturnValue(true);

      renderWithProviders(
        <ProtectedRoute requiredRoles={["Member", "Facilitator"]} requireAllRoles={false}>
          <TestComponent />
        </ProtectedRoute>,
        authState,
        mockUserProfile,
      );

      await waitFor(() => {
        expect(screen.getByText("Protected Content")).toBeInTheDocument();
      });

      expect(hasAnyRole).toHaveBeenCalledWith(mockUserProfile, ["Member", "Facilitator"]);
    });
  });

  describe("Minimum Role Level Access Control", () => {
    const authState = {
      token: "valid-token",
      refreshToken: "valid-refresh-token",
      user: null,
      userProfile: null,
      isAuthenticated: true,
    };

    it("should allow access when user meets minimum role level", async () => {
      const { hasMinimumRoleLevel } = require("../../../utils/permissions");
      hasMinimumRoleLevel.mockReturnValue(true);

      renderWithProviders(
        <ProtectedRoute minimumRole="Member">
          <TestComponent />
        </ProtectedRoute>,
        authState,
        mockUserProfile,
      );

      await waitFor(() => {
        expect(screen.getByText("Protected Content")).toBeInTheDocument();
      });

      expect(hasMinimumRoleLevel).toHaveBeenCalledWith(mockUserProfile, "Member");
    });

    it("should deny access when user does not meet minimum role level", async () => {
      const { hasMinimumRoleLevel } = require("../../../utils/permissions");
      hasMinimumRoleLevel.mockReturnValue(false);

      renderWithProviders(
        <ProtectedRoute minimumRole="Admin" showUnauthorizedMessage={true}>
          <TestComponent />
        </ProtectedRoute>,
        authState,
        mockUserProfile,
      );

      await waitFor(() => {
        expect(screen.getByText("Access Denied")).toBeInTheDocument();
      });

      expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
    });
  });

  describe("Custom Permission Check", () => {
    const authState = {
      token: "valid-token",
      refreshToken: "valid-refresh-token",
      user: null,
      userProfile: null,
      isAuthenticated: true,
    };

    it("should allow access when custom permission check returns true", async () => {
      const customCheck = jest.fn().mockReturnValue(true);

      renderWithProviders(
        <ProtectedRoute customPermissionCheck={customCheck}>
          <TestComponent />
        </ProtectedRoute>,
        authState,
        mockUserProfile,
      );

      await waitFor(() => {
        expect(screen.getByText("Protected Content")).toBeInTheDocument();
      });

      expect(customCheck).toHaveBeenCalledWith(mockUserProfile);
    });

    it("should deny access when custom permission check returns false", async () => {
      const customCheck = jest.fn().mockReturnValue(false);

      renderWithProviders(
        <ProtectedRoute customPermissionCheck={customCheck} showUnauthorizedMessage={true}>
          <TestComponent />
        </ProtectedRoute>,
        authState,
        mockUserProfile,
      );

      await waitFor(() => {
        expect(screen.getByText("Access Denied")).toBeInTheDocument();
      });

      expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
      expect(customCheck).toHaveBeenCalledWith(mockUserProfile);
    });
  });

  describe("Fallback and Error Handling", () => {
    it("should render custom fallback during loading", () => {
      const authState = {
        token: "valid-token",
        refreshToken: "valid-refresh-token",
        user: null,
        userProfile: null,
        isAuthenticated: true,
      };

      const CustomFallback = () => <div>Custom Loading...</div>;

      renderWithProviders(
        <ProtectedRoute fallback={<CustomFallback />}>
          <TestComponent />
        </ProtectedRoute>,
        authState,
      );

      expect(screen.getByText("Custom Loading...")).toBeInTheDocument();
    });

    it("should show user roles in unauthorized message", async () => {
      const { hasRole } = require("../../../utils/permissions");
      hasRole.mockReturnValue(false);

      const authState = {
        token: "valid-token",
        refreshToken: "valid-refresh-token",
        user: null,
        userProfile: null,
        isAuthenticated: true,
      };

      renderWithProviders(
        <ProtectedRoute requiredRole="Admin" showUnauthorizedMessage={true}>
          <TestComponent />
        </ProtectedRoute>,
        authState,
        mockUserProfile,
      );

      await waitFor(() => {
        expect(screen.getByText("Access Denied")).toBeInTheDocument();
        expect(screen.getByText(/Your current role: Member/)).toBeInTheDocument();
      });
    });

    it("should redirect instead of showing message when showUnauthorizedMessage is false", async () => {
      const { hasRole } = require("../../../utils/permissions");
      hasRole.mockReturnValue(false);

      const authState = {
        token: "valid-token",
        refreshToken: "valid-refresh-token",
        user: null,
        userProfile: null,
        isAuthenticated: true,
      };

      renderWithProviders(
        <ProtectedRoute requiredRole="Admin" showUnauthorizedMessage={false}>
          <TestComponent />
        </ProtectedRoute>,
        authState,
        mockUserProfile,
      );

      await waitFor(() => {
        expect(screen.queryByText("Access Denied")).not.toBeInTheDocument();
        expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
      });
    });
  });
});
