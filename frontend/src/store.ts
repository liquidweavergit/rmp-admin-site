import { configureStore } from "@reduxjs/toolkit";
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

// Auth types
interface UserCreate {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone?: string;
}

interface UserLogin {
  email: string;
  password: string;
}

interface UserResponse {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;
  is_active: boolean;
  is_verified: boolean;
  email_verified: boolean;
  phone_verified: boolean;
  created_at: string;
}

interface PermissionResponse {
  id: number;
  name: string;
  description: string;
  resource: string;
  action: string;
}

interface RoleResponse {
  id: number;
  name: string;
  description: string;
  priority: number;
  permissions: PermissionResponse[];
}

interface UserRoleResponse {
  role: RoleResponse;
  is_primary: boolean;
  assigned_at: string;
}

interface UserProfileResponse {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;
  is_active: boolean;
  is_verified: boolean;
  email_verified: boolean;
  phone_verified: boolean;
  created_at: string;
  roles: UserRoleResponse[];
  permissions: string[];
}

interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

interface AuthStatus {
  authenticated: boolean;
  user?: UserResponse;
}

// SMS Verification interfaces
interface SendSMSVerificationRequest {
  phone: string;
}

interface VerifySMSCodeRequest {
  phone: string;
  code: string;
}

interface SMSVerificationResponse {
  success: boolean;
  message: string;
  phone_verified?: boolean;
}

// Define the API base query
const baseQuery = fetchBaseQuery({
  baseUrl: process.env.REACT_APP_API_URL || "http://localhost:8000",
  prepareHeaders: (headers, { getState }) => {
    headers.set("content-type", "application/json");

    // Add auth token if available
    const token = (getState() as RootState).auth?.token;
    if (token) {
      headers.set("authorization", `Bearer ${token}`);
    }

    return headers;
  },
});

// Create the API slice
export const api = createApi({
  reducerPath: "api",
  baseQuery,
  tagTypes: ["User", "Circle", "Event", "Auth"],
  endpoints: (builder) => ({
    // Health check
    getHealth: builder.query<{ status: string }, void>({
      query: () => "/api/v1/health",
    }),

    // Authentication endpoints
    register: builder.mutation<UserResponse, UserCreate>({
      query: (userData) => ({
        url: "/api/v1/auth/register",
        method: "POST",
        body: userData,
      }),
      invalidatesTags: ["Auth"],
    }),

    login: builder.mutation<TokenResponse, UserLogin>({
      query: (loginData) => ({
        url: "/api/v1/auth/login",
        method: "POST",
        body: loginData,
      }),
      invalidatesTags: ["Auth"],
    }),

    logout: builder.mutation<void, { refresh_token: string }>({
      query: (logoutData) => ({
        url: "/api/v1/auth/logout",
        method: "POST",
        body: logoutData,
      }),
      invalidatesTags: ["Auth"],
    }),

    getCurrentUser: builder.query<UserResponse, void>({
      query: () => "/api/v1/auth/me",
      providesTags: ["Auth"],
    }),

    getAuthStatus: builder.query<AuthStatus, void>({
      query: () => "/api/v1/auth/status",
      providesTags: ["Auth"],
    }),

    getUserProfile: builder.query<UserProfileResponse, void>({
      query: () => "/api/v1/auth/profile",
      providesTags: ["Auth"],
    }),

    // SMS verification endpoints
    sendSMSVerification: builder.mutation<SMSVerificationResponse, SendSMSVerificationRequest>({
      query: (smsData) => ({
        url: "/api/v1/auth/send-sms-verification",
        method: "POST",
        body: smsData,
      }),
      invalidatesTags: ["Auth"],
    }),

    verifySMSCode: builder.mutation<SMSVerificationResponse, VerifySMSCodeRequest>({
      query: (verificationData) => ({
        url: "/api/v1/auth/verify-sms-code",
        method: "POST",
        body: verificationData,
      }),
      invalidatesTags: ["Auth"],
    }),
  }),
});

// Auth slice for token management
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

interface AuthState {
  token: string | null;
  refreshToken: string | null;
  user: UserResponse | null;
  userProfile: UserProfileResponse | null;
  isAuthenticated: boolean;
}

const initialState: AuthState = {
  token: localStorage.getItem("access_token"),
  refreshToken: localStorage.getItem("refresh_token"),
  user: null,
  userProfile: null,
  isAuthenticated: false,
};

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    setCredentials: (
      state,
      action: PayloadAction<{ tokens: TokenResponse; user?: UserResponse }>,
    ) => {
      const { tokens, user } = action.payload;
      state.token = tokens.access_token;
      state.refreshToken = tokens.refresh_token;
      state.isAuthenticated = true;
      if (user) {
        state.user = user;
      }

      // Store in localStorage
      localStorage.setItem("access_token", tokens.access_token);
      localStorage.setItem("refresh_token", tokens.refresh_token);
    },

    clearCredentials: (state) => {
      state.token = null;
      state.refreshToken = null;
      state.user = null;
      state.userProfile = null;
      state.isAuthenticated = false;

      // Clear localStorage
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
    },

    setUser: (state, action: PayloadAction<UserResponse>) => {
      state.user = action.payload;
      state.isAuthenticated = true;
    },

    setUserProfile: (state, action: PayloadAction<UserProfileResponse>) => {
      state.userProfile = action.payload;
      state.user = {
        id: action.payload.id,
        email: action.payload.email,
        first_name: action.payload.first_name,
        last_name: action.payload.last_name,
        phone: action.payload.phone,
        is_active: action.payload.is_active,
        is_verified: action.payload.is_verified,
        email_verified: action.payload.email_verified,
        phone_verified: action.payload.phone_verified,
        created_at: action.payload.created_at,
      };
      state.isAuthenticated = true;
    },
  },
});

export const { setCredentials, clearCredentials, setUser, setUserProfile } = authSlice.actions;

// Configure the store
export const store = configureStore({
  reducer: {
    [api.reducerPath]: api.reducer,
    auth: authSlice.reducer,
  },
  middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(api.middleware),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export const {
  useGetHealthQuery,
  useRegisterMutation,
  useLoginMutation,
  useLogoutMutation,
  useGetCurrentUserQuery,
  useGetAuthStatusQuery,
  useGetUserProfileQuery,
  useSendSMSVerificationMutation,
  useVerifySMSCodeMutation,
} = api;

// Export types for use in other modules
export type {
  UserCreate,
  UserLogin,
  UserResponse,
  PermissionResponse,
  RoleResponse,
  UserRoleResponse,
  UserProfileResponse,
  TokenResponse,
  AuthStatus,
  SendSMSVerificationRequest,
  VerifySMSCodeRequest,
  SMSVerificationResponse,
};
