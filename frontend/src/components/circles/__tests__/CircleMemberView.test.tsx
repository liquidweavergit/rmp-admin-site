import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import { ThemeProvider } from "@mui/material/styles";
import { createTheme } from "@mui/material/styles";
import "@testing-library/jest-dom";

import CircleMemberView from "../CircleMemberView";
import { api } from "../../../store";

// Mock date-fns to avoid timezone issues in tests
jest.mock("date-fns", () => ({
  format: jest.fn((date, formatStr) => {
    if (formatStr === "MMM d, yyyy h:mm a") return "Dec 19, 2024 7:00 PM";
    if (formatStr === "MMM d, yyyy") return "Dec 19, 2024";
    if (formatStr === "MMM d") return "Dec 10";
    return "mocked-date";
  }),
  parseISO: jest.fn((dateStr) => new Date(dateStr)),
  isAfter: jest.fn(() => true),
  isBefore: jest.fn(() => false),
  addDays: jest.fn((date, days) => new Date(date.getTime() + days * 24 * 60 * 60 * 1000)),
  differenceInDays: jest.fn(() => 7),
  startOfMonth: jest.fn(() => new Date("2024-12-01")),
  endOfMonth: jest.fn(() => new Date("2024-12-31")),
}));

// Mock data
const mockUserCircles = [
  {
    id: 1,
    name: "Men's Growth Circle",
    description: "A supportive circle for personal growth",
    facilitator_id: 2,
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
    facilitator_id: 3,
    capacity_min: 2,
    capacity_max: 6,
    location_name: "Office Building",
    location_address: "456 Oak Ave",
    meeting_schedule: { day: "Monday", time: "18:00" },
    status: "active",
    is_active: true,
    current_member_count: 4,
    created_at: "2024-01-15T00:00:00Z",
    updated_at: "2024-01-15T00:00:00Z",
  },
];

const mockMeetingHistory = {
  meetings: [
    {
      id: 1,
      title: "Weekly Check-in",
      description: "Regular circle meeting",
      scheduled_date: "2024-12-18T19:00:00Z",
      circle_id: 1,
      facilitator_id: 2,
      location_name: "Community Center",
      location_address: "123 Main St",
      agenda: { topics: ["introductions", "sharing"] },
      status: "completed",
      is_active: true,
      started_at: "2024-12-18T19:00:00Z",
      ended_at: "2024-12-18T21:00:00Z",
      meeting_notes: "Great session with good participation",
      duration_minutes: 120,
      attendance_summary: {
        total_expected: 5,
        total_present: 4,
        total_late: 1,
        total_absent: 0,
        attendance_rate: 80,
      },
      created_at: "2024-12-10T00:00:00Z",
      updated_at: "2024-12-18T21:00:00Z",
      user_attendance: {
        status: "present",
        checked_in_at: "2024-12-18T19:05:00Z",
        checked_out_at: "2024-12-18T21:00:00Z",
        notes: "Active participation",
      },
    },
    {
      id: 2,
      title: "Goal Setting Session",
      description: "Setting goals for the new year",
      scheduled_date: "2024-12-11T19:00:00Z",
      circle_id: 1,
      facilitator_id: 2,
      location_name: "Community Center",
      location_address: "123 Main St",
      agenda: { topics: ["goal setting", "accountability"] },
      status: "completed",
      is_active: true,
      started_at: "2024-12-11T19:00:00Z",
      ended_at: "2024-12-11T20:30:00Z",
      meeting_notes: "Productive goal-setting session",
      duration_minutes: 90,
      attendance_summary: {
        total_expected: 5,
        total_present: 5,
        total_late: 0,
        total_absent: 0,
        attendance_rate: 100,
      },
      created_at: "2024-12-05T00:00:00Z",
      updated_at: "2024-12-11T20:30:00Z",
      user_attendance: {
        status: "late",
        checked_in_at: "2024-12-11T19:15:00Z",
        checked_out_at: "2024-12-11T20:30:00Z",
        notes: "Arrived 15 minutes late but engaged well",
      },
    },
    {
      id: 3,
      title: "Monthly Reflection",
      description: "Reflecting on progress and challenges",
      scheduled_date: "2024-12-04T19:00:00Z",
      circle_id: 1,
      facilitator_id: 2,
      location_name: "Community Center",
      location_address: "123 Main St",
      agenda: { topics: ["reflection", "feedback"] },
      status: "completed",
      is_active: true,
      started_at: "2024-12-04T19:00:00Z",
      ended_at: "2024-12-04T20:45:00Z",
      meeting_notes: "Deep reflective session",
      duration_minutes: 105,
      attendance_summary: {
        total_expected: 5,
        total_present: 3,
        total_late: 0,
        total_absent: 2,
        attendance_rate: 60,
      },
      created_at: "2024-11-28T00:00:00Z",
      updated_at: "2024-12-04T20:45:00Z",
      user_attendance: {
        status: "absent",
        checked_in_at: null,
        checked_out_at: null,
        notes: "Family emergency - excused absence",
      },
    },
  ],
  total: 3,
  page: 1,
  per_page: 10,
};

const mockMembershipDetails = {
  user_id: 1,
  circle_id: 1,
  is_active: true,
  payment_status: "current",
  joined_at: "2024-01-01T00:00:00Z",
  membership_stats: {
    total_meetings_scheduled: 12,
    meetings_attended: 8,
    meetings_late: 2,
    meetings_absent: 2,
    attendance_rate: 67,
    current_streak: 3,
    longest_streak: 5,
  },
};

// Create a mock store with API slice
const createMockStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      [api.reducerPath]: api.reducer,
      auth: (
        state = {
          token: "mock-token",
          isAuthenticated: true,
          user: { id: 1, first_name: "John", last_name: "Doe", email: "john@example.com" },
        },
      ) => state,
    },
    middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(api.middleware),
    preloadedState: initialState,
  });
};

// Mock API responses
jest.mock("../../../store", () => ({
  ...jest.requireActual("../../../store"),
  useGetUserCirclesQuery: jest.fn(),
  useGetMeetingsQuery: jest.fn(),
  useGetCircleMembershipDetailsQuery: jest.fn(),
  useGetUserAttendanceQuery: jest.fn(),
}));

const theme = createTheme();

const renderWithProviders = (component: React.ReactElement, store = createMockStore()) => {
  return render(
    <Provider store={store}>
      <ThemeProvider theme={theme}>{component}</ThemeProvider>
    </Provider>,
  );
};

describe("CircleMemberView", () => {
  beforeEach(() => {
    jest.clearAllMocks();

    // Setup default mock implementations
    (require("../../../store").useGetUserCirclesQuery as jest.Mock).mockReturnValue({
      data: mockUserCircles,
      isLoading: false,
      error: null,
    });

    (require("../../../store").useGetMeetingsQuery as jest.Mock).mockReturnValue({
      data: mockMeetingHistory,
      isLoading: false,
      error: null,
    });

    (require("../../../store").useGetCircleMembershipDetailsQuery as jest.Mock).mockReturnValue({
      data: mockMembershipDetails,
      isLoading: false,
      error: null,
    });

    (require("../../../store").useGetUserAttendanceQuery as jest.Mock).mockReturnValue({
      data: mockMeetingHistory.meetings.map((m) => m.user_attendance),
      isLoading: false,
      error: null,
    });
  });

  describe("Component Rendering", () => {
    it("should render the member view title", () => {
      renderWithProviders(<CircleMemberView />);
      expect(screen.getByText("My Circle Journey")).toBeInTheDocument();
    });

    it("should display user circles list", () => {
      renderWithProviders(<CircleMemberView />);
      expect(screen.getByText("Men's Growth Circle")).toBeInTheDocument();
      expect(screen.getByText("Leadership Circle")).toBeInTheDocument();
    });

    it("should show circle selection interface", () => {
      renderWithProviders(<CircleMemberView />);
      expect(
        screen.getByText("Select a circle to view your participation history"),
      ).toBeInTheDocument();
    });
  });

  describe("Circle Selection", () => {
    it("should allow selecting a circle", async () => {
      renderWithProviders(<CircleMemberView />);

      const circleCard = screen.getByText("Men's Growth Circle").closest(".MuiCard-root");
      expect(circleCard).toBeInTheDocument();

      fireEvent.click(circleCard!);

      await waitFor(() => {
        expect(screen.getByText("Participation Summary")).toBeInTheDocument();
      });
    });

    it("should display circle details when selected", async () => {
      renderWithProviders(<CircleMemberView />);

      const circleCard = screen.getByText("Men's Growth Circle").closest(".MuiCard-root");
      fireEvent.click(circleCard!);

      await waitFor(() => {
        expect(screen.getByText("A supportive circle for personal growth")).toBeInTheDocument();
        // Use getAllByText to handle multiple "Community Center" elements and check the first one
        const communityElements = screen.getAllByText("Community Center");
        expect(communityElements.length).toBeGreaterThan(0);
      });
    });
  });

  describe("Participation Statistics", () => {
    it("should display membership statistics", async () => {
      renderWithProviders(<CircleMemberView />);

      const circleCard = screen.getByText("Men's Growth Circle").closest(".MuiCard-root");
      fireEvent.click(circleCard!);

      await waitFor(() => {
        expect(screen.getByText("67%")).toBeInTheDocument(); // attendance rate
        expect(screen.getByText("8")).toBeInTheDocument(); // meetings attended
        expect(screen.getByText("Current Streak: 3")).toBeInTheDocument();
      });
    });

    it("should show payment status", async () => {
      renderWithProviders(<CircleMemberView />);

      const circleCard = screen.getByText("Men's Growth Circle").closest(".MuiCard-root");
      fireEvent.click(circleCard!);

      await waitFor(() => {
        expect(screen.getByText("Current")).toBeInTheDocument(); // payment status
      });
    });

    it("should display attendance breakdown", async () => {
      renderWithProviders(<CircleMemberView />);

      const circleCard = screen.getByText("Men's Growth Circle").closest(".MuiCard-root");
      fireEvent.click(circleCard!);

      await waitFor(() => {
        expect(screen.getByText("8 Present")).toBeInTheDocument();
        expect(screen.getByText("2 Late")).toBeInTheDocument();
        expect(screen.getByText("2 Absent")).toBeInTheDocument();
      });
    });
  });

  describe("Meeting History", () => {
    it("should display meeting history list", async () => {
      renderWithProviders(<CircleMemberView />);

      const circleCard = screen.getByText("Men's Growth Circle").closest(".MuiCard-root");
      fireEvent.click(circleCard!);

      await waitFor(() => {
        expect(screen.getByText("Meeting History")).toBeInTheDocument();
        expect(screen.getByText("Weekly Check-in")).toBeInTheDocument();
        expect(screen.getByText("Goal Setting Session")).toBeInTheDocument();
        expect(screen.getByText("Monthly Reflection")).toBeInTheDocument();
      });
    });

    it("should show attendance status for each meeting", async () => {
      renderWithProviders(<CircleMemberView />);

      const circleCard = screen.getByText("Men's Growth Circle").closest(".MuiCard-root");
      fireEvent.click(circleCard!);

      await waitFor(() => {
        expect(screen.getByText("Present")).toBeInTheDocument();
        expect(screen.getByText("Late")).toBeInTheDocument();
        expect(screen.getByText("Absent")).toBeInTheDocument();
      });
    });

    it("should display meeting details when expanded", async () => {
      renderWithProviders(<CircleMemberView />);

      const circleCard = screen.getByText("Men's Growth Circle").closest(".MuiCard-root");
      fireEvent.click(circleCard!);

      await waitFor(() => {
        // Meeting items are rendered as ListItem components, not Card components
        const meetingItem = screen.getByText("Weekly Check-in").closest(".MuiListItem-root");
        fireEvent.click(meetingItem!);
      });

      await waitFor(() => {
        expect(screen.getByText("Active participation")).toBeInTheDocument();
        expect(screen.getByText("Great session with good participation")).toBeInTheDocument();
      });
    });
  });

  describe("Error States", () => {
    it("should handle loading state", () => {
      (require("../../../store").useGetUserCirclesQuery as jest.Mock).mockReturnValue({
        data: undefined,
        isLoading: true,
        error: null,
      });

      renderWithProviders(<CircleMemberView />);
      expect(screen.getByRole("progressbar")).toBeInTheDocument();
    });

    it("should handle error state", () => {
      (require("../../../store").useGetUserCirclesQuery as jest.Mock).mockReturnValue({
        data: undefined,
        isLoading: false,
        error: { message: "Failed to load circles" },
      });

      renderWithProviders(<CircleMemberView />);
      expect(screen.getByText(/error loading/i)).toBeInTheDocument();
    });

    it("should handle empty circles state", () => {
      (require("../../../store").useGetUserCirclesQuery as jest.Mock).mockReturnValue({
        data: [],
        isLoading: false,
        error: null,
      });

      renderWithProviders(<CircleMemberView />);
      expect(screen.getByText(/not currently a member/i)).toBeInTheDocument();
    });
  });

  describe("Filtering and Navigation", () => {
    it("should allow filtering meetings by date range", async () => {
      renderWithProviders(<CircleMemberView />);

      const circleCard = screen.getByText("Men's Growth Circle").closest(".MuiCard-root");
      fireEvent.click(circleCard!);

      await waitFor(() => {
        const filterButton = screen.getByText("Filter");
        fireEvent.click(filterButton);
      });

      expect(screen.getByText("Date Range")).toBeInTheDocument();
    });

    it("should support pagination for meeting history", async () => {
      const mockMeetingsWithPagination = {
        ...mockMeetingHistory,
        total: 25,
        page: 1,
        per_page: 10,
      };

      (require("../../../store").useGetMeetingsQuery as jest.Mock).mockReturnValue({
        data: mockMeetingsWithPagination,
        isLoading: false,
        error: null,
      });

      renderWithProviders(<CircleMemberView />);

      const circleCard = screen.getByText("Men's Growth Circle").closest(".MuiCard-root");
      fireEvent.click(circleCard!);

      await waitFor(() => {
        expect(screen.getByText("1-10 of 25")).toBeInTheDocument();
      });
    });
  });

  describe("Mobile Responsiveness", () => {
    it("should adapt layout for mobile view", () => {
      // Mock smaller viewport
      Object.defineProperty(window, "innerWidth", {
        writable: true,
        configurable: true,
        value: 390,
      });

      renderWithProviders(<CircleMemberView />);

      // Should still render core components
      expect(screen.getByText("My Circle Journey")).toBeInTheDocument();
    });
  });

  describe("Accessibility", () => {
    it("should have proper ARIA labels", () => {
      renderWithProviders(<CircleMemberView />);

      expect(screen.getByRole("main")).toBeInTheDocument();
      expect(screen.getByLabelText(/circle selection/i)).toBeInTheDocument();
    });

    it("should support keyboard navigation", async () => {
      renderWithProviders(<CircleMemberView />);

      const circleCard = screen.getByText("Men's Growth Circle").closest(".MuiCard-root");
      expect(circleCard).toBeVisible();

      // Should be focusable - cast to HTMLElement for focus method
      (circleCard as HTMLElement)?.focus();
      expect(circleCard).toHaveFocus();
    });
  });
});
