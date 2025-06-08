import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import { ThemeProvider } from "@mui/material/styles";
import "@testing-library/jest-dom";

import { LoginForm } from "../../../components/auth/LoginForm";
import { api } from "../../../store";
import { theme } from "../../../theme";

// Mock the store
const createMockStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      [api.reducerPath]: api.reducer,
      auth: (state = { token: null, refreshToken: null, user: null, isAuthenticated: false }) =>
        state,
    },
    middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(api.middleware),
    preloadedState: {
      auth: { token: null, refreshToken: null, user: null, isAuthenticated: false },
      ...initialState,
    },
  });
};

const renderLoginForm = (props = {}, storeState = {}) => {
  const store = createMockStore(storeState);
  const user = userEvent.setup();

  const defaultProps = {
    onSuccess: jest.fn(),
    onSwitchToRegister: jest.fn(),
    showTitle: true,
  };

  const utils = render(
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        <LoginForm {...defaultProps} {...props} />
      </ThemeProvider>
    </Provider>,
  );

  return {
    ...utils,
    user,
    store,
    props: { ...defaultProps, ...props },
  };
};

// Mock the useLoginMutation hook
const mockLoginMutation = jest.fn();
const mockUseLoginMutation = jest.fn();

jest.mock("../../../store", () => {
  const actual = jest.requireActual("../../../store");
  return {
    ...actual,
    useLoginMutation: () => mockUseLoginMutation(),
  };
});

describe("LoginForm", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockLoginMutation.mockReset();
    mockUseLoginMutation.mockReturnValue([mockLoginMutation, { isLoading: false }]);
  });

  describe("Rendering", () => {
    it("should render all form fields", () => {
      renderLoginForm();

      expect(screen.getByRole("textbox", { name: /email/i })).toBeInTheDocument();
      expect(screen.getByDisplayValue("")).toBeInTheDocument(); // password field
      expect(screen.getByRole("button", { name: /sign in/i })).toBeInTheDocument();
    });

    it("should render title when showTitle is true", () => {
      renderLoginForm({ showTitle: true });
      expect(screen.getByRole("heading", { name: /sign in/i })).toBeInTheDocument();
    });

    it("should not render title when showTitle is false", () => {
      renderLoginForm({ showTitle: false });
      expect(screen.queryByRole("heading", { name: /sign in/i })).not.toBeInTheDocument();
    });

    it("should render switch to register link when callback provided", () => {
      renderLoginForm();
      expect(screen.getByText(/don't have an account/i)).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /sign up here/i })).toBeInTheDocument();
    });

    it("should not render switch to register link when callback not provided", () => {
      renderLoginForm({ onSwitchToRegister: undefined });
      expect(screen.queryByText(/don't have an account/i)).not.toBeInTheDocument();
    });
  });

  describe("Form Interaction", () => {
    it("should allow typing in email field", async () => {
      const { user } = renderLoginForm();
      const emailInput = screen.getByRole("textbox", { name: /email/i });

      await user.type(emailInput, "test@example.com");
      expect(emailInput).toHaveValue("test@example.com");
    });

    it("should allow typing in password field", async () => {
      const { user } = renderLoginForm();
      const passwordInput = screen.getByLabelText("Password *");

      await user.type(passwordInput, "password123");
      expect(passwordInput).toHaveValue("password123");
    });

    it("should toggle password visibility", async () => {
      const { user } = renderLoginForm();
      const passwordInput = screen.getByLabelText("Password *");
      const toggleButton = screen.getByLabelText(/toggle password visibility/i);

      // Initially password should be hidden
      expect(passwordInput).toHaveAttribute("type", "password");

      // Click to show password
      await user.click(toggleButton);
      expect(passwordInput).toHaveAttribute("type", "text");

      // Click to hide password again
      await user.click(toggleButton);
      expect(passwordInput).toHaveAttribute("type", "password");
    });

    it("should call onSwitchToRegister when register link is clicked", async () => {
      const { user, props } = renderLoginForm();
      const registerLink = screen.getByRole("button", { name: /sign up here/i });

      await user.click(registerLink);
      expect(props.onSwitchToRegister).toHaveBeenCalledTimes(1);
    });
  });

  describe("Form Validation", () => {
    it("should show validation errors for empty fields", async () => {
      const { user } = renderLoginForm();
      const submitButton = screen.getByRole("button", { name: /sign in/i });

      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/email is required/i)).toBeInTheDocument();
        expect(screen.getByText(/password is required/i)).toBeInTheDocument();
      });
    });

    it("should show validation error for invalid email", async () => {
      const { user } = renderLoginForm();
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText("Password *");
      const submitButton = screen.getByRole("button", { name: /sign in/i });

      await user.type(emailInput, "invalid-email");
      await user.type(passwordInput, "password123");
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/please enter a valid email address/i)).toBeInTheDocument();
      });
    });

    it("should clear field errors when user starts typing", async () => {
      const { user } = renderLoginForm();
      const emailInput = screen.getByLabelText(/email/i);
      const submitButton = screen.getByRole("button", { name: /sign in/i });

      // Trigger validation error
      await user.click(submitButton);
      await waitFor(() => {
        expect(screen.getByText(/email is required/i)).toBeInTheDocument();
      });

      // Start typing to clear error
      await user.type(emailInput, "t");
      await waitFor(() => {
        expect(screen.queryByText(/email is required/i)).not.toBeInTheDocument();
      });
    });
  });

  describe("Form Submission", () => {
    it("should call login mutation with correct data on valid submission", async () => {
      const { user } = renderLoginForm();
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText("Password *");
      const submitButton = screen.getByRole("button", { name: /sign in/i });

      mockLoginMutation.mockResolvedValue({
        unwrap: () =>
          Promise.resolve({
            access_token: "mock-access-token",
            refresh_token: "mock-refresh-token",
            token_type: "bearer",
          }),
      });

      await user.type(emailInput, "test@example.com");
      await user.type(passwordInput, "Password123");
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockLoginMutation).toHaveBeenCalledWith({
          email: "test@example.com",
          password: "Password123",
        });
      });
    });

    it("should call onSuccess callback on successful login", async () => {
      const { user, props } = renderLoginForm();
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText("Password *");
      const submitButton = screen.getByRole("button", { name: /sign in/i });

      mockLoginMutation.mockResolvedValue({
        unwrap: () =>
          Promise.resolve({
            access_token: "mock-access-token",
            refresh_token: "mock-refresh-token",
            token_type: "bearer",
          }),
      });

      await user.type(emailInput, "test@example.com");
      await user.type(passwordInput, "Password123");
      await user.click(submitButton);

      await waitFor(() => {
        expect(props.onSuccess).toHaveBeenCalledTimes(1);
      });
    });

    it("should show error message on login failure", async () => {
      const { user } = renderLoginForm();
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText("Password *");
      const submitButton = screen.getByRole("button", { name: /sign in/i });

      mockLoginMutation.mockRejectedValue({
        status: 401,
        data: { detail: "Invalid credentials" },
      });

      await user.type(emailInput, "test@example.com");
      await user.type(passwordInput, "wrongpassword");
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
      });
    });

    it("should show generic error for 401 without detail", async () => {
      const { user } = renderLoginForm();
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText("Password *");
      const submitButton = screen.getByRole("button", { name: /sign in/i });

      mockLoginMutation.mockRejectedValue({
        status: 401,
      });

      await user.type(emailInput, "test@example.com");
      await user.type(passwordInput, "wrongpassword");
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/invalid email or password/i)).toBeInTheDocument();
      });
    });

    it("should prevent submission when form is invalid", async () => {
      const { user } = renderLoginForm();
      const submitButton = screen.getByRole("button", { name: /sign in/i });

      await user.click(submitButton);

      // Should not call the mutation
      expect(mockLoginMutation).not.toHaveBeenCalled();
    });
  });

  describe("Loading State", () => {
    it("should show loading state during submission", () => {
      // Mock loading state
      mockUseLoginMutation.mockReturnValue([mockLoginMutation, { isLoading: true }]);

      renderLoginForm();

      const submitButton = screen.getByRole("button", { name: /signing in/i });
      expect(submitButton).toBeDisabled();
      expect(screen.getByText(/signing in/i)).toBeInTheDocument();
    });
  });

  describe("Accessibility", () => {
    it("should have proper form labels and ARIA attributes", () => {
      renderLoginForm();

      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText("Password *");

      expect(emailInput).toHaveAttribute("type", "email");
      expect(emailInput).toHaveAttribute("autoComplete", "email");
      expect(emailInput).toHaveAttribute("required");

      expect(passwordInput).toHaveAttribute("type", "password");
      expect(passwordInput).toHaveAttribute("autoComplete", "current-password");
      expect(passwordInput).toHaveAttribute("required");
    });

    it("should have proper heading structure", () => {
      renderLoginForm();
      const heading = screen.getByRole("heading", { name: /sign in/i });
      expect(heading.tagName).toBe("H1");
    });
  });
});
