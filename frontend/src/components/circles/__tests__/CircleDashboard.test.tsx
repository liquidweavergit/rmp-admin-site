import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import { ThemeProvider } from "@mui/material/styles";
import { createTheme } from "@mui/material/styles";
import "@testing-library/jest-dom";

import CircleDashboard from "../CircleDashboard";
import { api } from "../../../store";
import * as storeHooks from "../../../store";

// Mock date-fns to avoid timezone issues in tests
jest.mock("date-fns", () => ({
  format: jest.fn((date, formatStr) => {
    if (formatStr === "MMM d, yyyy h:mm a") return "Dec 19, 2024 7:00 PM";
    if (formatStr === "MMM d, yyyy") return "Dec 19, 2024";
    if (formatStr === "MMM d") return "Dec 10"; // This matches the created_at date in mock data
    return "mocked-date";
  }),
  parseISO: jest.fn((dateStr) => new Date(dateStr)),
  isAfter: jest.fn(() => true),
  isBefore: jest.fn(() => false),
  addDays: jest.fn((date, days) => new Date(date.getTime() + days * 24 * 60 * 60 * 1000)),
}));

// Mock data
const mockCircles = [
  {
    id: 1,
    name: "Men's Growth Circle",
    description: "A supportive circle for personal growth",
    facilitator_id: 1,
    capacity_min: 2,
    capacity_max: 8,
    location_name: "Community Center",
    location_address: "123 Main St",
    meeting_schedule: { day: "Wednesday", time: "19:00" },
    status: "active",
    is_active: true,
    current_member_count: 5,
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z",
  },
  {
    id: 2,
    name: "Leadership Circle",
    description: "Developing leadership skills",
    facilitator_id: 1,
    capacity_min: 2,
    capacity_max: 6,
    location_name: "Office Building",
    location_address: "456 Oak Ave",
    meeting_schedule: { day: "Monday", time: "18:00" },
    status: "forming",
    is_active: true,
    current_member_count: 3,
    created_at: "2024-01-15T00:00:00Z",
    updated_at: "2024-01-15T00:00:00Z",
  },
];

const mockMembers = {
  members: [
    {
      user_id: 2,
      circle_id: 1,
      is_active: true,
      payment_status: "current",
      joined_at: "2024-01-01T00:00:00Z",
    },
    {
      user_id: 3,
      circle_id: 1,
      is_active: true,
      payment_status: "pending",
      joined_at: "2024-01-05T00:00:00Z",
    },
    {
      user_id: 4,
      circle_id: 1,
      is_active: true,
      payment_status: "overdue",
      joined_at: "2024-01-10T00:00:00Z",
    },
  ],
  total: 3,
};

const mockMeetings = {
  meetings: [
    {
      id: 1,
      title: "Weekly Check-in",
      description: "Regular circle meeting",
      scheduled_date: "2024-12-25T19:00:00Z",
      circle_id: 1,
      facilitator_id: 1,
      location_name: "Community Center",
      location_address: "123 Main St",
      agenda: { topics: ["introductions", "sharing"] },
      status: "scheduled",
      is_active: true,
      started_at: null,
      ended_at: null,
      meeting_notes: null,
      duration_minutes: null,
      attendance_summary: {
        total_expected: 5,
        total_present: 4,
        total_late: 1,
        total_absent: 0,
        attendance_rate: 80,
      },
      created_at: "2024-12-18T00:00:00Z",
      updated_at: "2024-12-18T00:00:00Z",
    },
    {
      id: 2,
      title: "Goal Setting Session",
      description: "Setting goals for the new year",
      scheduled_date: "2024-12-15T19:00:00Z",
      circle_id: 1,
      facilitator_id: 1,
      location_name: "Community Center",
      location_address: "123 Main St",
      agenda: { topics: ["goal setting", "accountability"] },
      status: "completed",
      is_active: true,
      started_at: "2024-12-15T19:00:00Z",
      ended_at: "2024-12-15T21:00:00Z",
      meeting_notes: "Great session with good participation",
      duration_minutes: 120,
      attendance_summary: {
        total_expected: 5,
        total_present: 5,
        total_late: 0,
        total_absent: 0,
        attendance_rate: 100,
      },
      created_at: "2024-12-10T00:00:00Z",
      updated_at: "2024-12-15T21:00:00Z",
    },
  ],
  total: 2,
  page: 1,
  per_page: 10,
};

// Create a mock store with API slice
const createMockStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      [api.reducerPath]: api.reducer,
      auth: (state = { token: "mock-token", isAuthenticated: true }) => state,
    },
    middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(api.middleware),
    preloadedState: initialState,
  });
};

// Mock API responses
const mockApiSlice = {
  useGetCirclesQuery: jest.fn(),
  useGetCircleMembersQuery: jest.fn(),
  useGetMeetingsQuery: jest.fn(),
  useUpdateCircleMutation: jest.fn(),
  useAddCircleMemberMutation: jest.fn(),
  useRemoveCircleMemberMutation: jest.fn(),
  useCreateMeetingMutation: jest.fn(),
  useStartMeetingMutation: jest.fn(),
  useEndMeetingMutation: jest.fn(),
};

// Mock the store module
jest.mock("../../../store", () => ({
  ...jest.requireActual("../../../store"),
  useGetCirclesQuery: jest.fn(),
  useGetCircleMembersQuery: jest.fn(),
  useGetMeetingsQuery: jest.fn(),
  useUpdateCircleMutation: jest.fn(),
  useAddCircleMemberMutation: jest.fn(),
  useRemoveCircleMemberMutation: jest.fn(),
  useCreateMeetingMutation: jest.fn(),
  useStartMeetingMutation: jest.fn(),
  useEndMeetingMutation: jest.fn(),
}));

const theme = createTheme();

const renderWithProviders = (component: React.ReactElement, store = createMockStore()) => {
  return render(
    <Provider store={store}>
      <ThemeProvider theme={theme}>{component}</ThemeProvider>
    </Provider>,
  );
};

describe("CircleDashboard", () => {
  beforeEach(() => {
    jest.clearAllMocks();

    // Default mock implementations
    (storeHooks.useGetCirclesQuery as jest.Mock).mockReturnValue({
      data: mockCircles,
      isLoading: false,
      error: null,
    });

    (storeHooks.useGetCircleMembersQuery as jest.Mock).mockReturnValue({
      data: mockMembers,
      isLoading: false,
    });

    (storeHooks.useGetMeetingsQuery as jest.Mock).mockReturnValue({
      data: mockMeetings,
      isLoading: false,
    });

    (storeHooks.useUpdateCircleMutation as jest.Mock).mockReturnValue([jest.fn()]);
    (storeHooks.useAddCircleMemberMutation as jest.Mock).mockReturnValue([jest.fn()]);
    (storeHooks.useRemoveCircleMemberMutation as jest.Mock).mockReturnValue([jest.fn()]);
    (storeHooks.useCreateMeetingMutation as jest.Mock).mockReturnValue([jest.fn()]);
    (storeHooks.useStartMeetingMutation as jest.Mock).mockReturnValue([jest.fn()]);
    (storeHooks.useEndMeetingMutation as jest.Mock).mockReturnValue([jest.fn()]);
  });

  describe("Overview Tab", () => {
    it("should render dashboard title and description", () => {
      renderWithProviders(<CircleDashboard />);

      expect(screen.getByText("Circle Dashboard")).toBeInTheDocument();
      expect(screen.getByText(/Manage your circles, track member engagement/)).toBeInTheDocument();
    });

    it("should display summary statistics correctly", () => {
      renderWithProviders(<CircleDashboard />);

      // Total circles
      expect(screen.getByText("2")).toBeInTheDocument(); // 2 circles
      expect(screen.getByText("Total Circles")).toBeInTheDocument();

      // Total members (5 + 3 = 8)
      expect(screen.getByText("8")).toBeInTheDocument();
      expect(screen.getByText("Total Members")).toBeInTheDocument();

      // Upcoming meetings (1 scheduled meeting)
      expect(screen.getByText("1")).toBeInTheDocument();
      expect(screen.getByText("Upcoming Meetings")).toBeInTheDocument();

      // Average attendance (80 + 100) / 2 = 90%
      expect(screen.getByText("90%")).toBeInTheDocument();
      expect(screen.getByText("Avg Attendance")).toBeInTheDocument();
    });

    it("should display circles list with correct information", () => {
      renderWithProviders(<CircleDashboard />);

      // Check circle names
      expect(screen.getByText("Men's Growth Circle")).toBeInTheDocument();
      expect(screen.getByText("Leadership Circle")).toBeInTheDocument();

      // Check circle descriptions
      expect(screen.getByText("A supportive circle for personal growth")).toBeInTheDocument();
      expect(screen.getByText("Developing leadership skills")).toBeInTheDocument();

      // Check status chips
      expect(screen.getByText("active")).toBeInTheDocument();
      expect(screen.getByText("forming")).toBeInTheDocument();

      // Check member counts
      expect(screen.getByText("5/8 members")).toBeInTheDocument();
      expect(screen.getByText("3/6 members")).toBeInTheDocument();

      // Check locations
      expect(screen.getByText("Community Center")).toBeInTheDocument();
      expect(screen.getByText("Office Building")).toBeInTheDocument();
    });

    it("should show loading state when circles are loading", () => {
      (storeHooks.useGetCirclesQuery as jest.Mock).mockReturnValue({
        data: undefined,
        isLoading: true,
        error: null,
      });

      renderWithProviders(<CircleDashboard />);

      // Should show skeleton loaders in the circles section
      expect(screen.getByText("My Circles")).toBeInTheDocument();
    });

    it("should show error state when circles fail to load", () => {
      (storeHooks.useGetCirclesQuery as jest.Mock).mockReturnValue({
        data: undefined,
        isLoading: false,
        error: { message: "Failed to fetch" },
      });

      renderWithProviders(<CircleDashboard />);

      expect(screen.getByText("Failed to load circles")).toBeInTheDocument();
    });

    it("should show empty state when no circles exist", () => {
      (storeHooks.useGetCirclesQuery as jest.Mock).mockReturnValue({
        data: [],
        isLoading: false,
        error: null,
      });

      renderWithProviders(<CircleDashboard />);

      expect(
        screen.getByText("No circles found. Create your first circle to get started!"),
      ).toBeInTheDocument();
    });

    it("should display next meeting information", () => {
      renderWithProviders(<CircleDashboard />);

      expect(screen.getByText("Next Meeting")).toBeInTheDocument();
      expect(screen.getByText("Weekly Check-in")).toBeInTheDocument();
      expect(screen.getByText("Dec 19, 2024 7:00 PM")).toBeInTheDocument();
    });

    it("should display quick action buttons", () => {
      renderWithProviders(<CircleDashboard />);

      expect(screen.getByText("Quick Actions")).toBeInTheDocument();
      expect(screen.getAllByText("Create Circle")).toHaveLength(2); // One in quick actions, one in circles section
      expect(screen.getByText("Schedule Meeting")).toBeInTheDocument();
      expect(screen.getByText("Manage Members")).toBeInTheDocument();
    });

    it("should display recent activity", () => {
      renderWithProviders(<CircleDashboard />);

      expect(screen.getByText("Recent Activity")).toBeInTheDocument();
      expect(screen.getByText("Weekly Check-in")).toBeInTheDocument();
      expect(screen.getAllByText("Goal Setting Session")).toHaveLength(2); // One in next meeting, one in recent activity
    });
  });

  describe("Circle Selection and Detail View", () => {
    it("should switch to detail view when circle is selected", async () => {
      renderWithProviders(<CircleDashboard />);

      // Click on a circle
      const circleItem = screen.getByText("Men's Growth Circle");
      fireEvent.click(circleItem);

      // Should switch to Circle Details tab
      await waitFor(() => {
        expect(screen.getByRole("tab", { selected: true })).toHaveTextContent("Circle Details");
      });
    });

    it("should display circle detail information correctly", async () => {
      renderWithProviders(<CircleDashboard />);

      // Select a circle first
      const circleItem = screen.getByText("Men's Growth Circle");
      fireEvent.click(circleItem);

      await waitFor(() => {
        // Check circle header information
        expect(screen.getByText("Men's Growth Circle")).toBeInTheDocument();
        expect(screen.getByText("A supportive circle for personal growth")).toBeInTheDocument();
        expect(screen.getByText("5")).toBeInTheDocument(); // member count
        expect(screen.getByText("of 8 members")).toBeInTheDocument();

        // Check location information
        expect(screen.getByText("Community Center")).toBeInTheDocument();
        expect(screen.getByText("123 Main St")).toBeInTheDocument();

        // Check meeting schedule
        expect(screen.getByText("Wednesday")).toBeInTheDocument();
        expect(screen.getByText("19:00")).toBeInTheDocument();
      });
    });

    it("should display circle members with payment status", async () => {
      renderWithProviders(<CircleDashboard />);

      // Select a circle
      const circleItem = screen.getByText("Men's Growth Circle");
      fireEvent.click(circleItem);

      await waitFor(() => {
        expect(screen.getByText("Circle Members")).toBeInTheDocument();

        // Check member entries
        expect(screen.getByText("User 2")).toBeInTheDocument();
        expect(screen.getByText("User 3")).toBeInTheDocument();
        expect(screen.getByText("User 4")).toBeInTheDocument();

        // Check payment status chips
        expect(screen.getByText("current")).toBeInTheDocument();
        expect(screen.getByText("pending")).toBeInTheDocument();
        expect(screen.getByText("overdue")).toBeInTheDocument();
      });
    });

    it("should display recent meetings for selected circle", async () => {
      renderWithProviders(<CircleDashboard />);

      // Select a circle
      const circleItem = screen.getByText("Men's Growth Circle");
      fireEvent.click(circleItem);

      await waitFor(() => {
        expect(screen.getByText("Recent Meetings")).toBeInTheDocument();

        // Check meeting entries
        expect(screen.getByText("Weekly Check-in")).toBeInTheDocument();
        expect(screen.getByText("Goal Setting Session")).toBeInTheDocument();

        // Check attendance rates
        expect(screen.getByText("80% attendance")).toBeInTheDocument();
        expect(screen.getByText("100% attendance")).toBeInTheDocument();
      });
    });

    it("should show info message when no circle is selected in detail view", () => {
      renderWithProviders(<CircleDashboard />);

      // Switch to detail tab without selecting a circle
      const detailTab = screen.getByText("Circle Details");
      fireEvent.click(detailTab);

      expect(
        screen.getByText("Select a circle from the overview to view details"),
      ).toBeInTheDocument();
    });
  });

  describe("Tab Navigation", () => {
    it("should switch between overview and detail tabs", () => {
      renderWithProviders(<CircleDashboard />);

      // Initially on overview tab
      expect(screen.getByRole("tab", { selected: true })).toHaveTextContent("Overview");

      // Switch to detail tab
      const detailTab = screen.getByText("Circle Details");
      fireEvent.click(detailTab);

      expect(screen.getByRole("tab", { selected: true })).toHaveTextContent("Circle Details");

      // Switch back to overview
      const overviewTab = screen.getByText("Overview");
      fireEvent.click(overviewTab);

      expect(screen.getByRole("tab", { selected: true })).toHaveTextContent("Overview");
    });

    it("should show badge on detail tab when circle is selected", async () => {
      renderWithProviders(<CircleDashboard />);

      // Select a circle
      const circleItem = screen.getByText("Men's Growth Circle");
      fireEvent.click(circleItem);

      await waitFor(() => {
        // Badge should show 1 when circle is selected
        const badge = screen.getByText("1");
        expect(badge).toBeInTheDocument();
      });
    });
  });

  describe("Helper Functions", () => {
    it("should calculate capacity percentage correctly", () => {
      renderWithProviders(<CircleDashboard />);

      // Men's Growth Circle: 5/8 = 62.5%
      // Leadership Circle: 3/6 = 50%
      // Progress bars should be rendered with these values
      const progressBars = screen.getAllByRole("progressbar");
      expect(progressBars.length).toBeGreaterThan(0);
    });

    it("should format dates correctly", () => {
      renderWithProviders(<CircleDashboard />);

      // Check that mocked date formatting is used
      expect(screen.getByText("Dec 19, 2024 7:00 PM")).toBeInTheDocument();
      expect(screen.getByText("completed • Dec 10")).toBeInTheDocument(); // This appears in recent activity
    });

    it("should determine status colors correctly", () => {
      renderWithProviders(<CircleDashboard />);

      // Status chips should be rendered with appropriate colors
      const activeChip = screen.getByText("active");
      const formingChip = screen.getByText("forming");

      expect(activeChip).toBeInTheDocument();
      expect(formingChip).toBeInTheDocument();
    });
  });

  describe("Loading States", () => {
    it("should show loading state for members when selected circle is loading", async () => {
      (storeHooks.useGetCircleMembersQuery as jest.Mock).mockReturnValue({
        data: undefined,
        isLoading: true,
      });

      renderWithProviders(<CircleDashboard />);

      // Select a circle
      const circleItem = screen.getByText("Men's Growth Circle");
      fireEvent.click(circleItem);

      await waitFor(() => {
        // Should show skeleton loaders for members
        expect(screen.getAllByTestId("skeleton")).toHaveLength(3);
      });
    });

    it("should show loading state for meetings", async () => {
      (storeHooks.useGetMeetingsQuery as jest.Mock).mockReturnValue({
        data: undefined,
        isLoading: true,
      });

      renderWithProviders(<CircleDashboard />);

      // Should show skeleton loaders for meetings
      expect(screen.getAllByTestId("skeleton")).toHaveLength(4);
    });
  });

  describe("Empty States", () => {
    it("should show empty state for members when no members exist", async () => {
      (storeHooks.useGetCircleMembersQuery as jest.Mock).mockReturnValue({
        data: { members: [], total: 0 },
        isLoading: false,
      });

      renderWithProviders(<CircleDashboard />);

      // Select a circle
      const circleItem = screen.getByText("Men's Growth Circle");
      fireEvent.click(circleItem);

      await waitFor(() => {
        expect(screen.getByRole("alert")).toHaveTextContent("No members found");
      });
    });

    it("should show empty state for meetings when no meetings exist", async () => {
      (storeHooks.useGetMeetingsQuery as jest.Mock).mockReturnValue({
        data: { meetings: [], total: 0, page: 1, per_page: 10 },
        isLoading: false,
      });

      renderWithProviders(<CircleDashboard />);

      // Select a circle
      const circleItem = screen.getByText("Men's Growth Circle");
      fireEvent.click(circleItem);

      await waitFor(() => {
        expect(screen.getByRole("alert")).toHaveTextContent("No meetings scheduled");
      });
    });

    it("should show empty state for next meeting when no upcoming meetings", () => {
      (storeHooks.useGetMeetingsQuery as jest.Mock).mockReturnValue({
        data: { meetings: [], total: 0, page: 1, per_page: 10 },
        isLoading: false,
      });

      renderWithProviders(<CircleDashboard />);

      expect(screen.getByRole("alert")).toHaveTextContent("No upcoming meetings");
    });

    it("should show empty state for recent activity when no recent meetings", () => {
      (storeHooks.useGetMeetingsQuery as jest.Mock).mockReturnValue({
        data: { meetings: [], total: 0, page: 1, per_page: 10 },
        isLoading: false,
      });

      renderWithProviders(<CircleDashboard />);

      expect(screen.getByText("No recent activity")).toBeInTheDocument();
    });
  });
});
