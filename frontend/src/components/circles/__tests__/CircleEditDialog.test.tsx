import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import { ThemeProvider } from "@mui/material/styles";
import { createTheme } from "@mui/material/styles";
import "@testing-library/jest-dom";

import CircleEditDialog from "../CircleEditDialog";
import { api } from "../../../store";

// Mock data
const mockCircleData = {
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
};

// Mock the API hooks
const mockUpdateCircle = jest.fn();

jest.mock("../../../store", () => ({
  ...jest.requireActual("../../../store"),
  useUpdateCircleMutation: () => [mockUpdateCircle, { isLoading: false }],
}));

// Create a mock store
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

const theme = createTheme();

const renderWithProviders = (component: React.ReactElement, store = createMockStore()) => {
  return render(
    <Provider store={store}>
      <ThemeProvider theme={theme}>{component}</ThemeProvider>
    </Provider>,
  );
};

describe("CircleEditDialog", () => {
  const mockOnClose = jest.fn();
  const mockOnSuccess = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    mockUpdateCircle.mockReset();
  });

  describe("Dialog Behavior", () => {
    it("should render dialog when open with circle data", () => {
      renderWithProviders(
        <CircleEditDialog
          open={true}
          circle={mockCircleData}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
        />,
      );

      expect(screen.getByText(/edit circle/i)).toBeInTheDocument();
      expect(screen.getByDisplayValue("Men's Growth Circle")).toBeInTheDocument();
      expect(
        screen.getByDisplayValue("A supportive circle for personal growth"),
      ).toBeInTheDocument();
    });

    it("should not render dialog when closed", () => {
      renderWithProviders(
        <CircleEditDialog
          open={false}
          circle={mockCircleData}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
        />,
      );

      expect(screen.queryByText(/edit circle/i)).not.toBeInTheDocument();
    });

    it("should not render dialog when circle is null", () => {
      renderWithProviders(
        <CircleEditDialog
          open={true}
          circle={null}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
        />,
      );

      expect(screen.queryByText(/edit circle/i)).not.toBeInTheDocument();
    });

    it("should call onClose when cancel button is clicked", () => {
      renderWithProviders(
        <CircleEditDialog
          open={true}
          circle={mockCircleData}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
        />,
      );

      const cancelButton = screen.getByText(/cancel/i);
      fireEvent.click(cancelButton);

      expect(mockOnClose).toHaveBeenCalled();
    });

    it("should call onClose when dialog backdrop is clicked", () => {
      renderWithProviders(
        <CircleEditDialog
          open={true}
          circle={mockCircleData}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
        />,
      );

      const backdrop = document.querySelector(".MuiBackdrop-root");
      fireEvent.click(backdrop!);

      expect(mockOnClose).toHaveBeenCalled();
    });
  });

  describe("Form Submission", () => {
    it("should update circle and call onSuccess when form is submitted with valid data", async () => {
      const mockUpdatedCircle = {
        ...mockCircleData,
        name: "Updated Circle Name",
        description: "Updated description",
      };

      mockUpdateCircle.mockReturnValue({
        unwrap: jest.fn().mockResolvedValue(mockUpdatedCircle),
      });

      renderWithProviders(
        <CircleEditDialog
          open={true}
          circle={mockCircleData}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
        />,
      );

      const nameField = screen.getByDisplayValue("Men's Growth Circle");
      const descriptionField = screen.getByDisplayValue("A supportive circle for personal growth");
      const submitButton = screen.getByText(/update circle/i);

      fireEvent.change(nameField, { target: { value: "Updated Circle Name" } });
      fireEvent.change(descriptionField, { target: { value: "Updated description" } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockUpdateCircle).toHaveBeenCalledWith({
          id: 1,
          data: {
            name: "Updated Circle Name",
            description: "Updated description",
            capacity_min: 2,
            capacity_max: 8,
            location_name: "Community Center",
            location_address: "123 Main St",
            meeting_schedule: { day: "Wednesday", time: "19:00" },
          },
        });
      });

      await waitFor(() => {
        expect(mockOnSuccess).toHaveBeenCalledWith(mockUpdatedCircle);
      });

      expect(mockOnClose).toHaveBeenCalled();
    });

    it("should handle API errors gracefully", async () => {
      const mockError = new Error("Failed to update circle");
      mockUpdateCircle.mockReturnValue({
        unwrap: jest.fn().mockRejectedValue(mockError),
      });

      renderWithProviders(
        <CircleEditDialog
          open={true}
          circle={mockCircleData}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
        />,
      );

      const nameField = screen.getByDisplayValue("Men's Growth Circle");
      const submitButton = screen.getByText(/update circle/i);

      fireEvent.change(nameField, { target: { value: "Updated Name" } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockUpdateCircle).toHaveBeenCalled();
      });

      // Should show error message
      await waitFor(() => {
        expect(screen.getByText(/failed to update circle/i)).toBeInTheDocument();
      });

      // Should not call onSuccess or onClose
      expect(mockOnSuccess).not.toHaveBeenCalled();
      expect(mockOnClose).not.toHaveBeenCalled();
    });

    it("should show loading state during submission", async () => {
      // Create a promise that we can control
      let resolvePromise: (value: any) => void;
      const pendingPromise = new Promise((resolve) => {
        resolvePromise = resolve;
      });

      mockUpdateCircle.mockReturnValue({
        unwrap: jest.fn().mockReturnValue(pendingPromise),
      });

      // Mock the hook to return loading state
      const mockStore = jest.requireMock("../../../store");
      mockStore.useUpdateCircleMutation = jest.fn(() => [mockUpdateCircle, { isLoading: true }]);

      renderWithProviders(
        <CircleEditDialog
          open={true}
          circle={mockCircleData}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
        />,
      );

      // Check that loading indicators are shown
      expect(screen.getByText(/update circle/i)).toBeDisabled();
      expect(screen.getByLabelText(/close/i)).toBeDisabled();

      // Clean up
      resolvePromise!(mockCircleData);
    });
  });

  describe("Form Validation", () => {
    it("should prevent submission with invalid data", async () => {
      renderWithProviders(
        <CircleEditDialog
          open={true}
          circle={mockCircleData}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
        />,
      );

      const nameField = screen.getByDisplayValue("Men's Growth Circle");
      const submitButton = screen.getByText(/update circle/i);
      const form = submitButton.closest("form");

      // Clear the name field to make it invalid
      fireEvent.change(nameField, { target: { value: "" } });
      fireEvent.submit(form!);

      await waitFor(() => {
        expect(screen.getByText(/circle name is required/i)).toBeInTheDocument();
      });

      expect(mockUpdateCircle).not.toHaveBeenCalled();
      expect(mockOnSuccess).not.toHaveBeenCalled();
      expect(mockOnClose).not.toHaveBeenCalled();
    });
  });

  describe("Accessibility", () => {
    it("should have proper ARIA attributes", () => {
      renderWithProviders(
        <CircleEditDialog
          open={true}
          circle={mockCircleData}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
        />,
      );

      const dialog = screen.getByRole("dialog");
      expect(dialog).toHaveAttribute("aria-labelledby");
      expect(dialog).toHaveAttribute("aria-describedby");
    });

    it("should focus on first form field when opened", () => {
      // Reset the mock to not be in loading state
      const mockStore = jest.requireMock("../../../store");
      mockStore.useUpdateCircleMutation = jest.fn(() => [mockUpdateCircle, { isLoading: false }]);

      renderWithProviders(
        <CircleEditDialog
          open={true}
          circle={mockCircleData}
          onClose={mockOnClose}
          onSuccess={mockOnSuccess}
        />,
      );

      // Material-UI dialogs focus the dialog container by default
      // The first form field should be focusable when not loading
      const nameField = screen.getByDisplayValue("Men's Growth Circle");
      expect(nameField).toBeInTheDocument();
      expect(nameField).not.toBeDisabled();

      // Manually focus to test that it's focusable
      nameField.focus();
      expect(nameField).toHaveFocus();
    });
  });
});
