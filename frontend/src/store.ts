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

// Google OAuth interfaces
interface GoogleOAuthUrlRequest {
  redirect_uri: string;
}

interface GoogleOAuthUrlResponse {
  authorization_url: string;
  state?: string;
}

interface GoogleOAuthCallbackRequest {
  code: string;
  state?: string;
  redirect_uri: string;
}

interface GoogleOAuthLoginRequest {
  id_token: string;
  access_token?: string;
}

interface GoogleOAuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: UserResponse;
}

// Circle-related interfaces
interface CircleCreate {
  name: string;
  description?: string;
  capacity_min?: number;
  capacity_max?: number;
  location_name?: string;
  location_address?: string;
  meeting_schedule?: Record<string, any>;
}

interface CircleUpdate {
  name?: string;
  description?: string;
  capacity_min?: number;
  capacity_max?: number;
  location_name?: string;
  location_address?: string;
  meeting_schedule?: Record<string, any>;
  status?: string;
  is_active?: boolean;
}

interface CircleResponse {
  id: number;
  name: string;
  description?: string;
  facilitator_id: number;
  capacity_min: number;
  capacity_max: number;
  location_name?: string;
  location_address?: string;
  meeting_schedule?: Record<string, any>;
  status: string;
  is_active: boolean;
  current_member_count: number;
  created_at: string;
  updated_at: string;
}

interface CircleMemberAdd {
  user_id: number;
  payment_status?: string;
}

interface CircleMemberResponse {
  user_id: number;
  circle_id: number;
  is_active: boolean;
  payment_status: string;
  joined_at: string;
}

interface CircleMemberListResponse {
  members: CircleMemberResponse[];
  total: number;
}

interface CircleMemberTransfer {
  target_circle_id: number;
  reason?: string;
}

interface CircleMemberPaymentUpdate {
  payment_status: string;
}

interface CircleSearchParams {
  page?: number;
  per_page?: number;
  search?: string;
  status?: string;
  facilitator_id?: number;
  location?: string;
  capacity_min?: number;
  capacity_max?: number;
  sort_by?: string;
  sort_order?: string;
}

// Meeting-related interfaces
interface MeetingCreate {
  title: string;
  description?: string;
  scheduled_date: string;
  circle_id: number;
  facilitator_id?: number;
  location_name?: string;
  location_address?: string;
  agenda?: Record<string, any>;
}

interface AttendanceSummary {
  total_expected: number;
  total_present: number;
  total_late: number;
  total_absent: number;
  attendance_rate: number;
}

interface MeetingResponse {
  id: number;
  title: string;
  description?: string;
  scheduled_date: string;
  circle_id: number;
  facilitator_id: number;
  location_name?: string;
  location_address?: string;
  agenda?: Record<string, any>;
  status: string;
  is_active: boolean;
  started_at?: string;
  ended_at?: string;
  meeting_notes?: string;
  duration_minutes?: number;
  attendance_summary: AttendanceSummary;
  created_at: string;
  updated_at: string;
}

interface MeetingListResponse {
  meetings: MeetingResponse[];
  total: number;
  page: number;
  per_page: number;
}

interface MeetingSearchParams {
  page?: number;
  per_page?: number;
  circle_id?: number;
  facilitator_id?: number;
  status?: string;
  date_from?: string;
  date_to?: string;
  search?: string;
}

// Additional interfaces for CircleMemberView
interface UserAttendanceResponse {
  status: "present" | "late" | "absent";
  checked_in_at?: string;
  checked_out_at?: string;
  notes?: string;
}

interface MeetingWithAttendanceResponse extends MeetingResponse {
  user_attendance?: UserAttendanceResponse;
}

interface MembershipStatsResponse {
  total_meetings_scheduled: number;
  meetings_attended: number;
  meetings_late: number;
  meetings_absent: number;
  attendance_rate: number;
  current_streak: number;
  longest_streak: number;
}

interface CircleMembershipDetailsResponse {
  user_id: number;
  circle_id: number;
  is_active: boolean;
  payment_status: string;
  joined_at: string;
  membership_stats: MembershipStatsResponse;
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
  tagTypes: ["User", "Circle", "Event", "Auth", "Meeting"],
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

    // Google OAuth endpoints
    getGoogleAuthUrl: builder.mutation<GoogleOAuthUrlResponse, GoogleOAuthUrlRequest>({
      query: (oauthData) => ({
        url: "/api/v1/auth/google/auth-url",
        method: "POST",
        body: oauthData,
      }),
    }),

    googleOAuthCallback: builder.mutation<GoogleOAuthResponse, GoogleOAuthCallbackRequest>({
      query: (callbackData) => ({
        url: "/api/v1/auth/google/callback",
        method: "POST",
        body: callbackData,
      }),
      invalidatesTags: ["Auth"],
    }),

    googleOAuthLogin: builder.mutation<GoogleOAuthResponse, GoogleOAuthLoginRequest>({
      query: (loginData) => ({
        url: "/api/v1/auth/google/login",
        method: "POST",
        body: loginData,
      }),
      invalidatesTags: ["Auth"],
    }),

    // Circle endpoints
    getCircles: builder.query<CircleResponse[], CircleSearchParams | void>({
      query: (searchParams) => {
        const params = new URLSearchParams();
        if (searchParams) {
          Object.entries(searchParams).forEach(([key, value]) => {
            if (value !== undefined && value !== null) {
              params.append(key, value.toString());
            }
          });
        }
        return `/api/v1/circles?${params.toString()}`;
      },
      providesTags: ["Circle"],
    }),

    getCircle: builder.query<CircleResponse, number>({
      query: (circleId) => `/api/v1/circles/${circleId}`,
      providesTags: (result, error, circleId) => [{ type: "Circle", id: circleId }],
    }),

    createCircle: builder.mutation<CircleResponse, CircleCreate>({
      query: (circleData) => ({
        url: "/api/v1/circles",
        method: "POST",
        body: circleData,
      }),
      invalidatesTags: ["Circle"],
    }),

    updateCircle: builder.mutation<CircleResponse, { id: number; data: CircleUpdate }>({
      query: ({ id, data }) => ({
        url: `/api/v1/circles/${id}`,
        method: "PUT",
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [{ type: "Circle", id }],
    }),

    getCircleMembers: builder.query<CircleMemberListResponse, number>({
      query: (circleId) => `/api/v1/circles/${circleId}/members`,
      providesTags: (result, error, circleId) => [{ type: "Circle", id: circleId }, "Circle"],
    }),

    addCircleMember: builder.mutation<
      CircleMemberResponse,
      { circleId: number; member: CircleMemberAdd }
    >({
      query: ({ circleId, member }) => ({
        url: `/api/v1/circles/${circleId}/members`,
        method: "POST",
        body: member,
      }),
      invalidatesTags: (result, error, { circleId }) => [{ type: "Circle", id: circleId }],
    }),

    removeCircleMember: builder.mutation<void, { circleId: number; userId: number }>({
      query: ({ circleId, userId }) => ({
        url: `/api/v1/circles/${circleId}/members/${userId}`,
        method: "DELETE",
      }),
      invalidatesTags: (result, error, { circleId }) => [{ type: "Circle", id: circleId }],
    }),

    transferCircleMember: builder.mutation<
      CircleMemberResponse,
      { circleId: number; userId: number; transfer_data: CircleMemberTransfer }
    >({
      query: ({ circleId, userId, transfer_data }) => ({
        url: `/api/v1/circles/${circleId}/members/${userId}/transfer`,
        method: "POST",
        body: transfer_data,
      }),
      invalidatesTags: (result, error, { circleId }) => [
        { type: "Circle", id: circleId },
        "Circle",
      ],
    }),

    updateMemberPaymentStatus: builder.mutation<
      CircleMemberResponse,
      { circleId: number; userId: number; payment_data: CircleMemberPaymentUpdate }
    >({
      query: ({ circleId, userId, payment_data }) => ({
        url: `/api/v1/circles/${circleId}/members/${userId}/payment`,
        method: "PATCH",
        body: payment_data,
      }),
      invalidatesTags: (result, error, { circleId }) => [{ type: "Circle", id: circleId }],
    }),

    // Meeting endpoints
    getMeetings: builder.query<MeetingListResponse, MeetingSearchParams | void>({
      query: (searchParams) => {
        const params = new URLSearchParams();
        if (searchParams) {
          Object.entries(searchParams).forEach(([key, value]) => {
            if (value !== undefined && value !== null) {
              params.append(key, value.toString());
            }
          });
        }
        return `/api/v1/meetings?${params.toString()}`;
      },
      providesTags: ["Meeting"],
    }),

    getMeeting: builder.query<MeetingResponse, number>({
      query: (meetingId) => `/api/v1/meetings/${meetingId}`,
      providesTags: (result, error, meetingId) => [{ type: "Meeting", id: meetingId }],
    }),

    createMeeting: builder.mutation<MeetingResponse, MeetingCreate>({
      query: (meetingData) => ({
        url: "/api/v1/meetings",
        method: "POST",
        body: meetingData,
      }),
      invalidatesTags: ["Meeting", "Circle"],
    }),

    startMeeting: builder.mutation<MeetingResponse, number>({
      query: (meetingId) => ({
        url: `/api/v1/meetings/${meetingId}/start`,
        method: "POST",
      }),
      invalidatesTags: (result, error, meetingId) => [{ type: "Meeting", id: meetingId }],
    }),

    endMeeting: builder.mutation<MeetingResponse, number>({
      query: (meetingId) => ({
        url: `/api/v1/meetings/${meetingId}/end`,
        method: "POST",
      }),
      invalidatesTags: (result, error, meetingId) => [{ type: "Meeting", id: meetingId }],
    }),

    cancelMeeting: builder.mutation<MeetingResponse, number>({
      query: (meetingId) => ({
        url: `/api/v1/meetings/${meetingId}/cancel`,
        method: "POST",
      }),
      invalidatesTags: (result, error, meetingId) => [{ type: "Meeting", id: meetingId }],
    }),

    // New endpoints for CircleMemberView
    getUserCircles: builder.query<CircleResponse[], void>({
      query: () => "/api/v1/users/me/circles",
      providesTags: ["Circle"],
    }),

    getCircleMembershipDetails: builder.query<CircleMembershipDetailsResponse, number>({
      query: (circleId) => `/api/v1/circles/${circleId}/membership/me`,
      providesTags: (result, error, circleId) => [{ type: "Circle", id: circleId }],
    }),

    getUserAttendance: builder.query<UserAttendanceResponse[], number>({
      query: (circleId) => `/api/v1/circles/${circleId}/meetings/attendance/me`,
      providesTags: (result, error, circleId) => [
        { type: "Meeting", id: `attendance-${circleId}` },
      ],
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
  useGetGoogleAuthUrlMutation,
  useGoogleOAuthCallbackMutation,
  useGoogleOAuthLoginMutation,
  useGetCirclesQuery,
  useGetCircleQuery,
  useCreateCircleMutation,
  useUpdateCircleMutation,
  useGetCircleMembersQuery,
  useAddCircleMemberMutation,
  useRemoveCircleMemberMutation,
  useTransferCircleMemberMutation,
  useUpdateMemberPaymentStatusMutation,
  useGetMeetingsQuery,
  useGetMeetingQuery,
  useCreateMeetingMutation,
  useStartMeetingMutation,
  useEndMeetingMutation,
  useCancelMeetingMutation,
  useGetUserCirclesQuery,
  useGetCircleMembershipDetailsQuery,
  useGetUserAttendanceQuery,
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
  GoogleOAuthUrlRequest,
  GoogleOAuthUrlResponse,
  GoogleOAuthCallbackRequest,
  GoogleOAuthLoginRequest,
  GoogleOAuthResponse,
  CircleCreate,
  CircleUpdate,
  CircleResponse,
  CircleMemberAdd,
  CircleMemberResponse,
  CircleMemberListResponse,
  CircleMemberTransfer,
  CircleMemberPaymentUpdate,
  CircleSearchParams,
  MeetingCreate,
  AttendanceSummary,
  MeetingResponse,
  MeetingListResponse,
  MeetingSearchParams,
  UserAttendanceResponse,
  MeetingWithAttendanceResponse,
  MembershipStatsResponse,
  CircleMembershipDetailsResponse,
};
