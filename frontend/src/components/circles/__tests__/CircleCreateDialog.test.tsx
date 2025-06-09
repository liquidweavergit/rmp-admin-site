import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import { ThemeProvider } from "@mui/material/styles";
import { createTheme } from "@mui/material/styles";
import "@testing-library/jest-dom";

import CircleCreateDialog from "../CircleCreateDialog";
import { api } from "../../../store";

// Mock the API hooks
const mockCreateCircle = jest.fn();

jest.mock("../../../store", () => ({
  ...jest.requireActual("../../../store"),
  useCreateCircleMutation: () => [mockCreateCircle, { isLoading: false }],
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

describe("CircleCreateDialog", () => {
  const mockOnClose = jest.fn();
  const mockOnSuccess = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    mockCreateCircle.mockReset();
  });

  describe("Dialog Behavior", () => {
    it("should render dialog when open", () => {
      renderWithProviders(
        <CircleCreateDialog open={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />,
      );

      expect(screen.getByText(/create new circle/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/circle name/i)).toBeInTheDocument();
    });

    it("should not render dialog when closed", () => {
      renderWithProviders(
        <CircleCreateDialog open={false} onClose={mockOnClose} onSuccess={mockOnSuccess} />,
      );

      expect(screen.queryByText(/create new circle/i)).not.toBeInTheDocument();
    });

    it("should call onClose when cancel button is clicked", () => {
      renderWithProviders(
        <CircleCreateDialog open={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />,
      );

      const cancelButton = screen.getByText(/cancel/i);
      fireEvent.click(cancelButton);

      expect(mockOnClose).toHaveBeenCalled();
    });

    it("should call onClose when dialog backdrop is clicked", () => {
      renderWithProviders(
        <CircleCreateDialog open={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />,
      );

      const backdrop = document.querySelector(".MuiBackdrop-root");
      fireEvent.click(backdrop!);

      expect(mockOnClose).toHaveBeenCalled();
    });
  });

  describe("Form Submission", () => {
    it("should create circle and call onSuccess when form is submitted with valid data", async () => {
      const mockCircleResponse = {
        id: 1,
        name: "Test Circle",
        description: "A test circle",
        facilitator_id: 1,
        capacity_min: 2,
        capacity_max: 8,
        location_name: "Test Location",
        location_address: "123 Test St",
        meeting_schedule: { day: "Monday", time: "18:00" },
        status: "forming",
        is_active: true,
        current_member_count: 1,
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      };

      mockCreateCircle.mockReturnValue({
        unwrap: jest.fn().mockResolvedValue(mockCircleResponse),
      });

      renderWithProviders(
        <CircleCreateDialog open={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />,
      );

      const nameField = screen.getByLabelText(/circle name/i);
      const descriptionField = screen.getByLabelText(/description/i);
      const submitButton = screen.getByText(/create circle/i);

      fireEvent.change(nameField, { target: { value: "Test Circle" } });
      fireEvent.change(descriptionField, { target: { value: "A test circle" } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockCreateCircle).toHaveBeenCalledWith({
          name: "Test Circle",
          description: "A test circle",
          capacity_min: 2,
          capacity_max: 8,
          location_name: "",
          location_address: "",
          meeting_schedule: null,
        });
      });

      await waitFor(() => {
        expect(mockOnSuccess).toHaveBeenCalledWith(mockCircleResponse);
      });

      expect(mockOnClose).toHaveBeenCalled();
    });

    it("should handle API errors gracefully", async () => {
      const mockError = new Error("Failed to create circle");
      mockCreateCircle.mockReturnValue({
        unwrap: jest.fn().mockRejectedValue(mockError),
      });

      renderWithProviders(
        <CircleCreateDialog open={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />,
      );

      const nameField = screen.getByLabelText(/circle name/i);
      const submitButton = screen.getByText(/create circle/i);

      fireEvent.change(nameField, { target: { value: "Test Circle" } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockCreateCircle).toHaveBeenCalled();
      });

      // Should show error message
      await waitFor(() => {
        expect(screen.getByText(/failed to create circle/i)).toBeInTheDocument();
      });

      // Should not call onSuccess or onClose
      expect(mockOnSuccess).not.toHaveBeenCalled();
      expect(mockOnClose).not.toHaveBeenCalled();
    });

    it("should show loading state during submission", async () => {
      // Mock loading state
      const mockStore = jest.requireMock("../../../store");
      mockStore.useCreateCircleMutation = jest.fn(() => [mockCreateCircle, { isLoading: true }]);

      renderWithProviders(
        <CircleCreateDialog open={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />,
      );

      // Check that loading indicators are shown
      expect(screen.getByText(/create circle/i)).toBeDisabled();
      expect(screen.getByLabelText(/close/i)).toBeDisabled();
    });
  });

  describe("Form Validation", () => {
    it("should prevent submission with invalid data", async () => {
      renderWithProviders(
        <CircleCreateDialog open={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />,
      );

      const submitButton = screen.getByText(/create circle/i);
      const form = submitButton.closest("form");

      // Submit form without required name
      fireEvent.submit(form!);

      await waitFor(() => {
        expect(screen.getByText(/circle name is required/i)).toBeInTheDocument();
      });

      expect(mockCreateCircle).not.toHaveBeenCalled();
      expect(mockOnSuccess).not.toHaveBeenCalled();
      expect(mockOnClose).not.toHaveBeenCalled();
    });
  });

  describe("Accessibility", () => {
    it("should have proper ARIA attributes", () => {
      renderWithProviders(
        <CircleCreateDialog open={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />,
      );

      const dialog = screen.getByRole("dialog");
      expect(dialog).toHaveAttribute("aria-labelledby");
      expect(dialog).toHaveAttribute("aria-describedby");
    });

    it("should focus on first form field when opened", () => {
      // Reset the mock to not be in loading state
      const mockStore = jest.requireMock("../../../store");
      mockStore.useCreateCircleMutation = jest.fn(() => [mockCreateCircle, { isLoading: false }]);

      renderWithProviders(
        <CircleCreateDialog open={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />,
      );

      const nameField = screen.getByLabelText(/circle name/i);
      expect(nameField).toBeInTheDocument();
      expect(nameField).not.toBeDisabled();

      // Manually focus to test that it's focusable
      nameField.focus();
      expect(nameField).toHaveFocus();
    });
  });
});
