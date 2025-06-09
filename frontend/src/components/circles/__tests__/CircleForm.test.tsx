import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import { ThemeProvider } from "@mui/material/styles";
import { createTheme } from "@mui/material/styles";
import "@testing-library/jest-dom";

import CircleForm from "../CircleForm";
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

describe("CircleForm", () => {
  const mockOnSubmit = jest.fn();
  const mockOnCancel = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("Create Mode", () => {
    it("should render form fields for creating a new circle", () => {
      renderWithProviders(
        <CircleForm
          mode="create"
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
          isLoading={false}
        />,
      );

      expect(screen.getByLabelText(/circle name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/minimum capacity/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/maximum capacity/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/location name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/location address/i)).toBeInTheDocument();
      expect(screen.getByText(/create circle/i)).toBeInTheDocument();
      expect(screen.getByText(/cancel/i)).toBeInTheDocument();
    });

    it("should have default values for capacity fields", () => {
      renderWithProviders(
        <CircleForm
          mode="create"
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
          isLoading={false}
        />,
      );

      const minCapacityField = screen.getByLabelText(/minimum capacity/i) as HTMLInputElement;
      const maxCapacityField = screen.getByLabelText(/maximum capacity/i) as HTMLInputElement;

      expect(minCapacityField.value).toBe("2");
      expect(maxCapacityField.value).toBe("8");
    });

    it("should call onSubmit with form data when create button is clicked", async () => {
      renderWithProviders(
        <CircleForm
          mode="create"
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
          isLoading={false}
        />,
      );

      const nameField = screen.getByLabelText(/circle name/i);
      const descriptionField = screen.getByLabelText(/description/i);
      const submitButton = screen.getByText(/create circle/i);

      fireEvent.change(nameField, { target: { value: "New Circle" } });
      fireEvent.change(descriptionField, { target: { value: "A new circle for growth" } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith({
          name: "New Circle",
          description: "A new circle for growth",
          capacity_min: 2,
          capacity_max: 8,
          location_name: "",
          location_address: "",
          meeting_schedule: null,
        });
      });
    });

    it("should validate required fields", async () => {
      renderWithProviders(
        <CircleForm
          mode="create"
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
          isLoading={false}
        />,
      );

      const submitButton = screen.getByText(/create circle/i);
      const form = submitButton.closest("form");

      // Submit the form directly to trigger validation
      fireEvent.submit(form!);

      await waitFor(() => {
        expect(screen.getByText(/circle name is required/i)).toBeInTheDocument();
      });

      expect(mockOnSubmit).not.toHaveBeenCalled();
    });

    it("should validate capacity constraints", async () => {
      renderWithProviders(
        <CircleForm
          mode="create"
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
          isLoading={false}
        />,
      );

      const nameField = screen.getByLabelText(/circle name/i);
      const minCapacityField = screen.getByLabelText(/minimum capacity/i);
      const maxCapacityField = screen.getByLabelText(/maximum capacity/i);
      const submitButton = screen.getByText(/create circle/i);
      const form = submitButton.closest("form");

      fireEvent.change(nameField, { target: { value: "Test Circle" } });
      fireEvent.change(minCapacityField, { target: { value: "8" } });
      fireEvent.change(maxCapacityField, { target: { value: "6" } });
      fireEvent.submit(form!);

      await waitFor(() => {
        expect(
          screen.getByText(/maximum capacity must be greater than or equal to minimum capacity/i),
        ).toBeInTheDocument();
      });

      expect(mockOnSubmit).not.toHaveBeenCalled();
    });
  });

  describe("Edit Mode", () => {
    it("should render form fields for editing an existing circle", () => {
      renderWithProviders(
        <CircleForm
          mode="edit"
          initialData={mockCircleData}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
          isLoading={false}
        />,
      );

      expect(screen.getByLabelText(/circle name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/minimum capacity/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/maximum capacity/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/location name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/location address/i)).toBeInTheDocument();
      expect(screen.getByText(/update circle/i)).toBeInTheDocument();
      expect(screen.getByText(/cancel/i)).toBeInTheDocument();
    });

    it("should populate form fields with initial data", () => {
      renderWithProviders(
        <CircleForm
          mode="edit"
          initialData={mockCircleData}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
          isLoading={false}
        />,
      );

      const nameField = screen.getByLabelText(/circle name/i) as HTMLInputElement;
      const descriptionField = screen.getByLabelText(/description/i) as HTMLInputElement;
      const minCapacityField = screen.getByLabelText(/minimum capacity/i) as HTMLInputElement;
      const maxCapacityField = screen.getByLabelText(/maximum capacity/i) as HTMLInputElement;
      const locationNameField = screen.getByLabelText(/location name/i) as HTMLInputElement;
      const locationAddressField = screen.getByLabelText(/location address/i) as HTMLInputElement;

      expect(nameField.value).toBe("Men's Growth Circle");
      expect(descriptionField.value).toBe("A supportive circle for personal growth");
      expect(minCapacityField.value).toBe("2");
      expect(maxCapacityField.value).toBe("8");
      expect(locationNameField.value).toBe("Community Center");
      expect(locationAddressField.value).toBe("123 Main St");
    });

    it("should call onSubmit with updated form data when update button is clicked", async () => {
      renderWithProviders(
        <CircleForm
          mode="edit"
          initialData={mockCircleData}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
          isLoading={false}
        />,
      );

      const nameField = screen.getByLabelText(/circle name/i);
      const submitButton = screen.getByText(/update circle/i);

      fireEvent.change(nameField, { target: { value: "Updated Circle Name" } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith({
          name: "Updated Circle Name",
          description: "A supportive circle for personal growth",
          capacity_min: 2,
          capacity_max: 8,
          location_name: "Community Center",
          location_address: "123 Main St",
          meeting_schedule: { day: "Wednesday", time: "19:00" },
        });
      });
    });
  });

  describe("Form Interactions", () => {
    it("should call onCancel when cancel button is clicked", () => {
      renderWithProviders(
        <CircleForm
          mode="create"
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
          isLoading={false}
        />,
      );

      const cancelButton = screen.getByText(/cancel/i);
      fireEvent.click(cancelButton);

      expect(mockOnCancel).toHaveBeenCalled();
    });

    it("should disable form fields and buttons when loading", () => {
      renderWithProviders(
        <CircleForm
          mode="create"
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
          isLoading={true}
        />,
      );

      const nameField = screen.getByLabelText(/circle name/i);
      const submitButton = screen.getByText(/create circle/i);
      const cancelButton = screen.getByText(/cancel/i);

      expect(nameField).toBeDisabled();
      expect(submitButton).toBeDisabled();
      expect(cancelButton).toBeDisabled();
    });

    it("should show loading indicator when loading", () => {
      renderWithProviders(
        <CircleForm
          mode="create"
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
          isLoading={true}
        />,
      );

      expect(screen.getByRole("progressbar")).toBeInTheDocument();
    });
  });

  describe("Meeting Schedule", () => {
    it("should include meeting schedule fields", () => {
      renderWithProviders(
        <CircleForm
          mode="create"
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
          isLoading={false}
        />,
      );

      expect(screen.getByText(/meeting schedule/i)).toBeInTheDocument();
      expect(screen.getByRole("combobox", { name: /day of week/i })).toBeInTheDocument();
      expect(screen.getByLabelText(/meeting time/i)).toBeInTheDocument();
    });

    it("should handle meeting schedule data correctly", async () => {
      renderWithProviders(
        <CircleForm
          mode="create"
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
          isLoading={false}
        />,
      );

      const nameField = screen.getByLabelText(/circle name/i);
      const dayField = screen.getByRole("combobox", { name: /day of week/i });
      const timeField = screen.getByLabelText(/meeting time/i);
      const submitButton = screen.getByText(/create circle/i);

      fireEvent.change(nameField, { target: { value: "Test Circle" } });

      // For Material-UI Select, we need to click to open and then select
      fireEvent.mouseDown(dayField);
      const mondayOption = await screen.findByText("Monday");
      fireEvent.click(mondayOption);

      fireEvent.change(timeField, { target: { value: "18:00" } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith({
          name: "Test Circle",
          description: "",
          capacity_min: 2,
          capacity_max: 8,
          location_name: "",
          location_address: "",
          meeting_schedule: {
            day: "Monday",
            time: "18:00",
          },
        });
      });
    });
  });
});
