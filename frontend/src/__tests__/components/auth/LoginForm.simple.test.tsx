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

// Create a simple mock store
const createMockStore = () => {
  return configureStore({
    reducer: {
      [api.reducerPath]: api.reducer,
      auth: (state = { token: null, refreshToken: null, user: null, isAuthenticated: false }) =>
        state,
    },
    middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(api.middleware),
  });
};

const renderLoginForm = (props = {}) => {
  const store = createMockStore();
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

describe("LoginForm - Core Functionality", () => {
  describe("Rendering", () => {
    it("should render all essential form elements", () => {
      renderLoginForm();

      // Check for email input
      expect(screen.getByRole("textbox", { name: /email/i })).toBeInTheDocument();

      // Check for password input (using data-testid approach)
      expect(screen.getByDisplayValue("")).toBeInTheDocument();

      // Check for submit button
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

    it("should render register link when callback provided", () => {
      renderLoginForm();
      expect(screen.getByText(/don't have an account/i)).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /sign up here/i })).toBeInTheDocument();
    });
  });

  describe("Form Interaction", () => {
    it("should allow typing in email field", async () => {
      const { user } = renderLoginForm();
      const emailInput = screen.getByRole("textbox", { name: /email/i });

      await user.type(emailInput, "test@example.com");
      expect(emailInput).toHaveValue("test@example.com");
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
      const emailInput = screen.getByRole("textbox", { name: /email/i });
      const submitButton = screen.getByRole("button", { name: /sign in/i });

      await user.type(emailInput, "invalid-email");
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/please enter a valid email address/i)).toBeInTheDocument();
      });
    });
  });

  describe("Accessibility", () => {
    it("should have proper form labels and attributes", () => {
      renderLoginForm();

      const emailInput = screen.getByRole("textbox", { name: /email/i });
      expect(emailInput).toHaveAttribute("type", "email");
      expect(emailInput).toHaveAttribute("autoComplete", "email");
      expect(emailInput).toHaveAttribute("required");
    });

    it("should have proper heading structure", () => {
      renderLoginForm();
      const heading = screen.getByRole("heading", { name: /sign in/i });
      expect(heading.tagName).toBe("H1");
    });
  });
});
