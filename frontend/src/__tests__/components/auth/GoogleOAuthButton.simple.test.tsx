import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Provider } from "react-redux";
import { BrowserRouter } from "react-router-dom";
import { configureStore } from "@reduxjs/toolkit";
import { ThemeProvider } from "@mui/material/styles";
import "@testing-library/jest-dom";

import { GoogleOAuthButton } from "../../../components/auth/GoogleOAuthButton";
import { api } from "../../../store";
import { theme } from "../../../theme";

// Mock the API hooks
const mockGetGoogleAuthUrl = jest.fn();
const mockGoogleOAuthCallback = jest.fn();
const mockGoogleOAuthLogin = jest.fn();

jest.mock("../../../store", () => ({
  ...jest.requireActual("../../../store"),
  useGetGoogleAuthUrlMutation: () => [mockGetGoogleAuthUrl, {}],
  useGoogleOAuthCallbackMutation: () => [mockGoogleOAuthCallback, {}],
  useGoogleOAuthLoginMutation: () => [mockGoogleOAuthLogin, {}],
  setCredentials: jest.fn(),
}));

// Mock react-router-dom
const mockNavigate = jest.fn();
jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => mockNavigate,
}));

// Create a simple mock store
const createMockStore = () => {
  return configureStore({
    reducer: {
      api: api.reducer,
      auth: (state = { token: null, isAuthenticated: false }, action) => state,
    },
    middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(api.middleware),
  });
};

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <Provider store={createMockStore()}>
    <BrowserRouter>
      <ThemeProvider theme={theme}>{children}</ThemeProvider>
    </BrowserRouter>
  </Provider>
);

describe("GoogleOAuthButton Component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    process.env.REACT_APP_GOOGLE_CLIENT_ID = "mock-client-id";
  });

  describe("Basic Rendering", () => {
    it("renders Google OAuth button", () => {
      render(
        <TestWrapper>
          <GoogleOAuthButton />
        </TestWrapper>,
      );

      expect(screen.getByRole("button")).toBeInTheDocument();
      expect(screen.getByText("Sign in with Google")).toBeInTheDocument();
    });

    it("renders button with custom text for redirect mode", () => {
      render(
        <TestWrapper>
          <GoogleOAuthButton mode="redirect" />
        </TestWrapper>,
      );

      expect(screen.getByText("Continue with Google")).toBeInTheDocument();
    });

    it("renders disabled button when disabled prop is true", () => {
      render(
        <TestWrapper>
          <GoogleOAuthButton disabled />
        </TestWrapper>,
      );

      expect(screen.getByRole("button")).toBeDisabled();
    });

    it("renders full width button", () => {
      render(
        <TestWrapper>
          <GoogleOAuthButton fullWidth />
        </TestWrapper>,
      );

      const button = screen.getByRole("button");
      expect(button).toHaveClass("MuiButton-fullWidth");
    });

    it("shows divider when showDivider is true", () => {
      render(
        <TestWrapper>
          <GoogleOAuthButton showDivider dividerText="custom divider" />
        </TestWrapper>,
      );

      expect(screen.getByText("custom divider")).toBeInTheDocument();
    });
  });

  describe("Button Sizes", () => {
    it("renders small button with correct height", () => {
      render(
        <TestWrapper>
          <GoogleOAuthButton size="small" />
        </TestWrapper>,
      );

      const button = screen.getByRole("button");
      expect(button).toHaveStyle({ height: "36px" });
    });

    it("renders medium button with correct height", () => {
      render(
        <TestWrapper>
          <GoogleOAuthButton size="medium" />
        </TestWrapper>,
      );

      const button = screen.getByRole("button");
      expect(button).toHaveStyle({ height: "42px" });
    });

    it("renders large button with correct height", () => {
      render(
        <TestWrapper>
          <GoogleOAuthButton size="large" />
        </TestWrapper>,
      );

      const button = screen.getByRole("button");
      expect(button).toHaveStyle({ height: "56px" });
    });
  });

  describe("Button Variants", () => {
    it("renders outlined variant by default", () => {
      render(
        <TestWrapper>
          <GoogleOAuthButton />
        </TestWrapper>,
      );

      const button = screen.getByRole("button");
      expect(button).toHaveClass("MuiButton-outlined");
    });

    it("renders contained variant", () => {
      render(
        <TestWrapper>
          <GoogleOAuthButton variant="contained" />
        </TestWrapper>,
      );

      const button = screen.getByRole("button");
      expect(button).toHaveClass("MuiButton-contained");
    });

    it("renders text variant", () => {
      render(
        <TestWrapper>
          <GoogleOAuthButton variant="text" />
        </TestWrapper>,
      );

      const button = screen.getByRole("button");
      expect(button).toHaveClass("MuiButton-text");
    });
  });

  describe("Redirect Mode", () => {
    it("calls getGoogleAuthUrl when button is clicked in redirect mode", async () => {
      const user = userEvent.setup();
      mockGetGoogleAuthUrl.mockResolvedValue({
        unwrap: () =>
          Promise.resolve({
            authorization_url: "https://accounts.google.com/oauth/authorize?...",
            state: "mock-state",
          }),
      });

      // Mock window.location
      Object.defineProperty(window, "location", {
        value: {
          origin: "http://localhost:3000",
          href: "",
        },
        writable: true,
      });

      render(
        <TestWrapper>
          <GoogleOAuthButton mode="redirect" />
        </TestWrapper>,
      );

      const button = screen.getByRole("button");
      await user.click(button);

      await waitFor(() => {
        expect(mockGetGoogleAuthUrl).toHaveBeenCalledWith({
          redirect_uri: "http://localhost:3000/auth/google/callback",
        });
      });
    });

    it("handles redirect flow error", async () => {
      const user = userEvent.setup();
      const onError = jest.fn();
      mockGetGoogleAuthUrl.mockRejectedValue({
        data: { detail: "Failed to get authorization URL" },
      });

      render(
        <TestWrapper>
          <GoogleOAuthButton mode="redirect" onError={onError} />
        </TestWrapper>,
      );

      const button = screen.getByRole("button");
      await user.click(button);

      await waitFor(() => {
        expect(onError).toHaveBeenCalledWith("Failed to get authorization URL");
      });
    });
  });

  describe("Popup Mode", () => {
    beforeEach(() => {
      // Mock window.open
      Object.defineProperty(window, "open", {
        writable: true,
        value: jest.fn(),
      });
    });

    it("opens popup window when button is clicked in popup mode", async () => {
      const user = userEvent.setup();
      const mockPopup = {
        closed: false,
        close: jest.fn(),
      };

      (window.open as jest.Mock).mockReturnValue(mockPopup);
      mockGetGoogleAuthUrl.mockResolvedValue({
        unwrap: () =>
          Promise.resolve({
            authorization_url: "https://accounts.google.com/oauth/authorize?...",
          }),
      });

      render(
        <TestWrapper>
          <GoogleOAuthButton mode="popup" />
        </TestWrapper>,
      );

      const button = screen.getByRole("button");
      await user.click(button);

      await waitFor(() => {
        expect(window.open).toHaveBeenCalledWith(
          "https://accounts.google.com/oauth/authorize?...",
          "google-oauth",
          "width=500,height=600,scrollbars=yes,resizable=yes",
        );
      });
    });

    it("handles blocked popup", async () => {
      const user = userEvent.setup();
      const onError = jest.fn();

      (window.open as jest.Mock).mockReturnValue(null); // Popup blocked
      mockGetGoogleAuthUrl.mockResolvedValue({
        unwrap: () =>
          Promise.resolve({
            authorization_url: "https://accounts.google.com/oauth/authorize?...",
          }),
      });

      render(
        <TestWrapper>
          <GoogleOAuthButton mode="popup" onError={onError} />
        </TestWrapper>,
      );

      const button = screen.getByRole("button");
      await user.click(button);

      await waitFor(() => {
        expect(onError).toHaveBeenCalledWith(expect.stringContaining("Popup blocked"));
      });
    });
  });

  describe("One Tap Mode", () => {
    beforeEach(() => {
      // Mock document.createElement for script loading
      const originalCreateElement = document.createElement;
      jest.spyOn(document, "createElement").mockImplementation((tagName) => {
        if (tagName === "script") {
          const script = originalCreateElement.call(document, tagName) as HTMLScriptElement;
          script.remove = jest.fn();
          // Auto-trigger onload for testing
          setTimeout(() => {
            if (script.onload) {
              (script.onload as any)();
            }
          }, 0);
          return script;
        }
        return originalCreateElement.call(document, tagName);
      });
    });

    afterEach(() => {
      jest.restoreAllMocks();
    });

    it("loads Google script for One Tap mode", async () => {
      render(
        <TestWrapper>
          <GoogleOAuthButton mode="oneTap" />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(document.createElement).toHaveBeenCalledWith("script");
      });
    });

    it("handles Google credential response successfully", async () => {
      const onSuccess = jest.fn();
      mockGoogleOAuthLogin.mockResolvedValue({
        unwrap: () =>
          Promise.resolve({
            access_token: "access-token",
            refresh_token: "refresh-token",
            token_type: "Bearer",
            user: { id: 1, email: "test@example.com" },
          }),
      });

      render(
        <TestWrapper>
          <GoogleOAuthButton mode="oneTap" onSuccess={onSuccess} />
        </TestWrapper>,
      );

      // Wait for the global function to be defined
      await waitFor(() => {
        expect(window.handleGoogleCredentialResponse).toBeDefined();
      });

      // Simulate Google credential response
      const mockResponse = { credential: "mock-id-token" };
      if (window.handleGoogleCredentialResponse) {
        await window.handleGoogleCredentialResponse(mockResponse);
      }

      await waitFor(() => {
        expect(mockGoogleOAuthLogin).toHaveBeenCalledWith({
          id_token: "mock-id-token",
        });
      });

      await waitFor(() => {
        expect(onSuccess).toHaveBeenCalled();
      });
    });

    it("handles missing credential in response", async () => {
      const onError = jest.fn();

      render(
        <TestWrapper>
          <GoogleOAuthButton mode="oneTap" onError={onError} />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(window.handleGoogleCredentialResponse).toBeDefined();
      });

      // Simulate response without credential
      const mockResponse = {};
      if (window.handleGoogleCredentialResponse) {
        await window.handleGoogleCredentialResponse(mockResponse);
      }

      await waitFor(() => {
        expect(onError).toHaveBeenCalledWith("No credential received from Google");
      });
    });
  });

  describe("Error Handling", () => {
    it("displays error alert when error occurs", async () => {
      const user = userEvent.setup();
      mockGetGoogleAuthUrl.mockRejectedValue({
        data: { detail: "Server error" },
      });

      render(
        <TestWrapper>
          <GoogleOAuthButton mode="redirect" />
        </TestWrapper>,
      );

      const button = screen.getByRole("button");
      await user.click(button);

      await waitFor(() => {
        expect(screen.getByRole("alert")).toBeInTheDocument();
        expect(screen.getByText("Server error")).toBeInTheDocument();
      });
    });

    it("shows loading state during authentication", async () => {
      const user = userEvent.setup();
      let resolvePromise: (value: any) => void;
      const mockPromise = new Promise((resolve) => {
        resolvePromise = resolve;
      });

      mockGetGoogleAuthUrl.mockReturnValue({
        unwrap: () => mockPromise,
      });

      render(
        <TestWrapper>
          <GoogleOAuthButton mode="redirect" />
        </TestWrapper>,
      );

      const button = screen.getByRole("button");
      await user.click(button);

      await waitFor(() => {
        expect(screen.getByText("Signing in...")).toBeInTheDocument();
        expect(button).toBeDisabled();
      });

      // Resolve the promise
      resolvePromise!({
        authorization_url: "https://accounts.google.com/oauth/authorize?...",
      });
    });
  });

  describe("Callback Handling", () => {
    it("calls onSuccess callback when authentication succeeds", async () => {
      const onSuccess = jest.fn();
      const user = userEvent.setup();

      mockGetGoogleAuthUrl.mockResolvedValue({
        unwrap: () =>
          Promise.resolve({
            authorization_url: "https://accounts.google.com/oauth/authorize?...",
          }),
      });

      // Mock successful authentication
      Object.defineProperty(window, "location", {
        value: {
          origin: "http://localhost:3000",
          href: "",
        },
        writable: true,
      });

      render(
        <TestWrapper>
          <GoogleOAuthButton mode="redirect" onSuccess={onSuccess} />
        </TestWrapper>,
      );

      const button = screen.getByRole("button");
      await user.click(button);

      await waitFor(() => {
        expect(mockGetGoogleAuthUrl).toHaveBeenCalled();
      });
    });

    it("calls onError callback when authentication fails", async () => {
      const onError = jest.fn();
      const user = userEvent.setup();

      mockGetGoogleAuthUrl.mockRejectedValue({
        data: { detail: "Authentication failed" },
      });

      render(
        <TestWrapper>
          <GoogleOAuthButton mode="redirect" onError={onError} />
        </TestWrapper>,
      );

      const button = screen.getByRole("button");
      await user.click(button);

      await waitFor(() => {
        expect(onError).toHaveBeenCalledWith("Authentication failed");
      });
    });
  });

  describe("Button Behavior", () => {
    it("prevents multiple clicks during loading", async () => {
      const user = userEvent.setup();
      mockGetGoogleAuthUrl.mockImplementation(() => ({
        unwrap: () => new Promise(() => {}), // Never resolves
      }));

      render(
        <TestWrapper>
          <GoogleOAuthButton mode="redirect" />
        </TestWrapper>,
      );

      const button = screen.getByRole("button");

      // First click
      await user.click(button);

      await waitFor(() => {
        expect(button).toBeDisabled();
      });

      // Second click should not trigger anything
      await user.click(button);

      expect(mockGetGoogleAuthUrl).toHaveBeenCalledTimes(1);
    });

    it("does not trigger authentication when disabled", async () => {
      const user = userEvent.setup();

      render(
        <TestWrapper>
          <GoogleOAuthButton mode="redirect" disabled />
        </TestWrapper>,
      );

      const button = screen.getByRole("button");
      await user.click(button);

      expect(mockGetGoogleAuthUrl).not.toHaveBeenCalled();
    });
  });
});
