import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import { ThemeProvider } from "@mui/material/styles";
import { createTheme } from "@mui/material/styles";
import "@testing-library/jest-dom";

import MemberManagementInterface from "../MemberManagementInterface";
import { api } from "../../../store";

// Mock date-fns to ensure consistent test results
jest.mock("date-fns", () => ({
  format: jest.fn((date, formatStr) => {
    if (formatStr === "MMM d, yyyy") return "Dec 19, 2024";
    return "mocked-date";
  }),
  parseISO: jest.fn((dateStr) => new Date(dateStr)),
}));

const mockCircle = {
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
  current_member_count: 3,
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
};

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

const mockCircles = [
  mockCircle,
  {
    id: 2,
    name: "Leadership Circle",
    description: "Developing leadership skills",
    facilitator_id: 1,
    capacity_min: 2,
    capacity_max: 6,
    location_name: "Office Building",
    status: "active",
    is_active: true,
    current_member_count: 2,
    created_at: "2024-01-15T00:00:00Z",
    updated_at: "2024-01-15T00:00:00Z",
  },
];

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

jest.mock("../../../store", () => ({
  ...jest.requireActual("../../../store"),
  useGetCircleMembersQuery: jest.fn(),
  useGetCirclesQuery: jest.fn(),
  useAddCircleMemberMutation: jest.fn(),
  useRemoveCircleMemberMutation: jest.fn(),
  useTransferCircleMemberMutation: jest.fn(),
  useUpdateMemberPaymentStatusMutation: jest.fn(),
}));

const theme = createTheme();

const renderWithProviders = (component: React.ReactElement, store = createMockStore()) => {
  return render(
    <Provider store={store}>
      <ThemeProvider theme={theme}>{component}</ThemeProvider>
    </Provider>,
  );
};

describe("MemberManagementInterface", () => {
  const mockUseGetCircleMembersQuery = require("../../../store").useGetCircleMembersQuery;
  const mockUseGetCirclesQuery = require("../../../store").useGetCirclesQuery;
  const mockUseAddCircleMemberMutation = require("../../../store").useAddCircleMemberMutation;
  const mockUseRemoveCircleMemberMutation = require("../../../store").useRemoveCircleMemberMutation;
  const mockUseTransferCircleMemberMutation =
    require("../../../store").useTransferCircleMemberMutation;
  const mockUseUpdateMemberPaymentStatusMutation =
    require("../../../store").useUpdateMemberPaymentStatusMutation;

  const mockMutations = {
    addMember: jest.fn(),
    removeMember: jest.fn(),
    transferMember: jest.fn(),
    updatePaymentStatus: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();

    mockUseGetCircleMembersQuery.mockReturnValue({
      data: mockMembers,
      isLoading: false,
      error: null,
      refetch: jest.fn(),
    });

    mockUseGetCirclesQuery.mockReturnValue({
      data: mockCircles,
      isLoading: false,
      error: null,
    });

    mockUseAddCircleMemberMutation.mockReturnValue([
      mockMutations.addMember,
      { isLoading: false, error: null },
    ]);

    mockUseRemoveCircleMemberMutation.mockReturnValue([
      mockMutations.removeMember,
      { isLoading: false, error: null },
    ]);

    mockUseTransferCircleMemberMutation.mockReturnValue([
      mockMutations.transferMember,
      { isLoading: false, error: null },
    ]);

    mockUseUpdateMemberPaymentStatusMutation.mockReturnValue([
      mockMutations.updatePaymentStatus,
      { isLoading: false, error: null },
    ]);
  });

  describe("Component Rendering", () => {
    it("should render member management interface with all sections", () => {
      renderWithProviders(<MemberManagementInterface circle={mockCircle} />);

      expect(screen.getByText("Member Management")).toBeInTheDocument();
      expect(screen.getByText("Current Members")).toBeInTheDocument();
      expect(screen.getByText("Add New Member")).toBeInTheDocument();
    });

    it("should display all current members with their information", () => {
      renderWithProviders(<MemberManagementInterface circle={mockCircle} />);

      expect(screen.getByText("User 2")).toBeInTheDocument();
      expect(screen.getByText("User 3")).toBeInTheDocument();
      expect(screen.getByText("User 4")).toBeInTheDocument();

      expect(screen.getByText("current")).toBeInTheDocument();
      expect(screen.getAllByText("pending")).toHaveLength(2); // One in member list, one in form default
      expect(screen.getByText("overdue")).toBeInTheDocument();
    });

    it("should show loading state when members are loading", () => {
      mockUseGetCircleMembersQuery.mockReturnValue({
        data: undefined,
        isLoading: true,
        error: null,
        refetch: jest.fn(),
      });

      renderWithProviders(<MemberManagementInterface circle={mockCircle} />);

      expect(screen.getByTestId("loading-members")).toBeInTheDocument();
    });

    it("should show error state when members query fails", () => {
      mockUseGetCircleMembersQuery.mockReturnValue({
        data: undefined,
        isLoading: false,
        error: { status: 500, data: { detail: "Server error" } },
        refetch: jest.fn(),
      });

      renderWithProviders(<MemberManagementInterface circle={mockCircle} />);

      expect(screen.getByText(/error loading members/i)).toBeInTheDocument();
    });

    it("should show empty state when no members exist", () => {
      mockUseGetCircleMembersQuery.mockReturnValue({
        data: { members: [], total: 0 },
        isLoading: false,
        error: null,
        refetch: jest.fn(),
      });

      renderWithProviders(<MemberManagementInterface circle={mockCircle} />);

      expect(screen.getByText(/no members in this circle/i)).toBeInTheDocument();
    });
  });

  describe("Add Member Functionality", () => {
    it("should render add member form with required fields", () => {
      renderWithProviders(<MemberManagementInterface circle={mockCircle} />);

      expect(screen.getByLabelText(/user id/i)).toBeInTheDocument();
      expect(screen.getByDisplayValue("")).toBeInTheDocument(); // Payment status select
      expect(screen.getByRole("button", { name: /add member/i })).toBeInTheDocument();
    });

    it("should validate user ID input", async () => {
      renderWithProviders(<MemberManagementInterface circle={mockCircle} />);

      const addButton = screen.getByRole("button", { name: /add member/i });
      fireEvent.click(addButton);

      await waitFor(() => {
        expect(screen.getByText(/user id is required/i)).toBeInTheDocument();
      });
    });

    it("should successfully add a new member", async () => {
      mockMutations.addMember.mockResolvedValue({
        data: {
          user_id: 5,
          circle_id: 1,
          is_active: true,
          payment_status: "pending",
          joined_at: "2024-12-19T00:00:00Z",
        },
      });

      renderWithProviders(<MemberManagementInterface circle={mockCircle} />);

      const userIdInput = screen.getByLabelText(/user id/i);
      const paymentStatusSelect = screen.getByDisplayValue("");
      const addButton = screen.getByRole("button", { name: /add member/i });

      fireEvent.change(userIdInput, { target: { value: "5" } });
      fireEvent.mouseDown(paymentStatusSelect);
      fireEvent.click(screen.getAllByText("pending")[1]); // Click the dropdown option, not the chip
      fireEvent.click(addButton);

      await waitFor(() => {
        expect(mockMutations.addMember).toHaveBeenCalledWith({
          circleId: 1,
          member: { user_id: 5, payment_status: "pending" },
        });
      });
    });
  });

  describe("Remove Member Functionality", () => {
    it("should show remove buttons for each member", () => {
      renderWithProviders(<MemberManagementInterface circle={mockCircle} />);

      const removeButtons = screen.getAllByLabelText(/remove member/i);
      expect(removeButtons).toHaveLength(3);
    });

    it("should show confirmation dialog when removing member", async () => {
      renderWithProviders(<MemberManagementInterface circle={mockCircle} />);

      const removeButtons = screen.getAllByLabelText(/remove member/i);
      fireEvent.click(removeButtons[0]);

      await waitFor(() => {
        expect(screen.getByText(/confirm member removal/i)).toBeInTheDocument();
      });
    });

    it("should successfully remove a member", async () => {
      mockMutations.removeMember.mockResolvedValue({});

      renderWithProviders(<MemberManagementInterface circle={mockCircle} />);

      const removeButtons = screen.getAllByLabelText(/remove member/i);
      fireEvent.click(removeButtons[0]);

      await waitFor(() => {
        expect(screen.getByText(/confirm member removal/i)).toBeInTheDocument();
      });

      const confirmButton = screen.getByRole("button", { name: /confirm/i });
      fireEvent.click(confirmButton);

      await waitFor(() => {
        expect(mockMutations.removeMember).toHaveBeenCalledWith({
          circleId: 1,
          userId: 2,
        });
      });
    });
  });

  describe("Payment Status Update Functionality", () => {
    it("should show payment status update options for each member", () => {
      renderWithProviders(<MemberManagementInterface circle={mockCircle} />);

      const paymentMenuButtons = screen.getAllByLabelText(/update payment status/i);
      expect(paymentMenuButtons).toHaveLength(3);
    });

    it("should successfully update payment status", async () => {
      mockMutations.updatePaymentStatus.mockResolvedValue({
        data: {
          user_id: 2,
          circle_id: 1,
          is_active: true,
          payment_status: "overdue",
          joined_at: "2024-01-01T00:00:00Z",
        },
      });

      renderWithProviders(<MemberManagementInterface circle={mockCircle} />);

      const paymentMenuButtons = screen.getAllByLabelText(/update payment status/i);
      fireEvent.click(paymentMenuButtons[0]);

      const overdueOption = screen.getAllByText("overdue")[1]; // Get the menu item, not the chip
      fireEvent.click(overdueOption);

      await waitFor(() => {
        expect(mockMutations.updatePaymentStatus).toHaveBeenCalledWith({
          circleId: 1,
          userId: 2,
          payment_data: { payment_status: "overdue" },
        });
      });
    });
  });

  describe("Transfer Member Functionality", () => {
    it("should show transfer option for each member", () => {
      renderWithProviders(<MemberManagementInterface circle={mockCircle} />);

      const transferButtons = screen.getAllByLabelText(/transfer member/i);
      expect(transferButtons).toHaveLength(3);
    });

    it("should show transfer dialog with available circles", async () => {
      renderWithProviders(<MemberManagementInterface circle={mockCircle} />);

      const transferButtons = screen.getAllByLabelText(/transfer member/i);
      fireEvent.click(transferButtons[0]);

      await waitFor(() => {
        expect(screen.getByText(/transfer member/i)).toBeInTheDocument();
      });

      // Wait for circles to load and check if select is accessible
      await waitFor(() => {
        expect(screen.getByRole("combobox")).toBeInTheDocument();
      });
    });

    it("should successfully transfer a member", async () => {
      mockMutations.transferMember.mockResolvedValue({
        data: {
          user_id: 2,
          circle_id: 2,
          is_active: true,
          payment_status: "current",
          joined_at: "2024-12-19T00:00:00Z",
        },
      });

      renderWithProviders(<MemberManagementInterface circle={mockCircle} />);

      const transferButtons = screen.getAllByLabelText(/transfer member/i);
      fireEvent.click(transferButtons[0]);

      await waitFor(() => {
        expect(screen.getByText(/transfer member/i)).toBeInTheDocument();
      });

      const targetCircleSelect = screen.getByRole("combobox");
      fireEvent.mouseDown(targetCircleSelect);

      // Wait for dropdown to open and find the leadership circle option
      await waitFor(() => {
        expect(screen.getByText("Leadership Circle")).toBeInTheDocument();
      });
      fireEvent.click(screen.getByText("Leadership Circle"));

      const reasonInput = screen.getByLabelText(/reason/i);
      fireEvent.change(reasonInput, { target: { value: "Better fit for schedule" } });

      const transferButton = screen.getByRole("button", { name: /transfer/i });
      fireEvent.click(transferButton);

      await waitFor(() => {
        expect(mockMutations.transferMember).toHaveBeenCalledWith({
          circleId: 1,
          userId: 2,
          transfer_data: {
            target_circle_id: 2,
            reason: "Better fit for schedule",
          },
        });
      });
    });
  });

  describe("Accessibility", () => {
    it("should have proper ARIA labels for all interactive elements", () => {
      renderWithProviders(<MemberManagementInterface circle={mockCircle} />);

      expect(screen.getByLabelText(/user id/i)).toBeInTheDocument();
      expect(screen.getByDisplayValue("")).toBeInTheDocument(); // Payment status select
      expect(screen.getAllByLabelText(/remove member/i)).toHaveLength(3);
      expect(screen.getAllByLabelText(/update payment status/i)).toHaveLength(3);
      expect(screen.getAllByLabelText(/transfer member/i)).toHaveLength(3);
    });
  });
});
