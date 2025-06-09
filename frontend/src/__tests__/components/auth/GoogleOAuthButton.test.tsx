import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Provider } from "react-redux";
import { BrowserRouter } from "react-router-dom";
import { configureStore } from "@reduxjs/toolkit";
import { ThemeProvider } from "@mui/material/styles";
import "@testing-library/jest-dom";

import { GoogleOAuthButton } from "../../../components/auth/GoogleOAuthButton";
import { api, setCredentials } from "../../../store";
import { theme } from "../../../theme";

// Mock the API
const mockApi = {
  reducerPath: "api",
  reducer: (state = {}, action: any) => state,
  middleware: () => (next: any) => (action: any) => next(action),
  endpoints: {},
};

const createMockStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      api: mockApi.reducer,
      auth: (state = { token: null, isAuthenticated: false }, action) => {
        if (action.type === "auth/setCredentials") {
          return { ...state, token: "mock-token", isAuthenticated: true };
        }
        return state;
      },
    },
    middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(mockApi.middleware),
    preloadedState: {
      auth: { token: null, isAuthenticated: false },
      ...initialState,
    },
  });
};

const TestWrapper: React.FC<{ children: React.ReactNode; store?: any }> = ({
  children,
  store = createMockStore(),
}) => (
  <Provider store={store}>
    <BrowserRouter>
      <ThemeProvider theme={theme}>{children}</ThemeProvider>
    </BrowserRouter>
  </Provider>
);

// Mock mutations
const mockGetGoogleAuthUrl = jest.fn();
const mockGoogleOAuthCallback = jest.fn();
const mockGoogleOAuthLogin = jest.fn();

// Mock the API hooks
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

// Mock window.open
Object.defineProperty(window, "open", {
  writable: true,
  value: jest.fn(),
});

// Mock Google script loading
Object.defineProperty(document, "createElement", {
  writable: true,
  value: jest.fn().mockImplementation((tagName) => {
    if (tagName === "script") {
      const script = {
        src: "",
        async: false,
        defer: false,
        onload: null,
        remove: jest.fn(),
      };
      // Auto-trigger onload for testing
      setTimeout(() => {
        if (script.onload) script.onload();
      }, 0);
      return script;
    }
    return jest.requireActual("document").createElement(tagName);
  }),
});

describe("GoogleOAuthButton Component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    delete window.google;
    delete window.handleGoogleCredentialResponse;

    // Reset environment variables
    process.env.REACT_APP_GOOGLE_CLIENT_ID = "mock-client-id";
  });

  afterEach(() => {
    jest.clearAllTimers();
  });

  describe("Basic Rendering", () => {
    it("renders default OAuth button", () => {
      render(
        <TestWrapper>
          <GoogleOAuthButton />
        </TestWrapper>,
      );

      expect(screen.getByRole("button")).toBeInTheDocument();
      expect(screen.getByText("Sign in with Google")).toBeInTheDocument();
    });

    it("renders button with custom text for different modes", () => {
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

    it("renders with different sizes", () => {
      const { rerender } = render(
        <TestWrapper>
          <GoogleOAuthButton size="small" />
        </TestWrapper>,
      );

      let button = screen.getByRole("button");
      expect(button).toHaveStyle({ height: "36px" });

      rerender(
        <TestWrapper>
          <GoogleOAuthButton size="large" />
        </TestWrapper>,
      );

      button = screen.getByRole("button");
      expect(button).toHaveStyle({ height: "56px" });
    });

    it("renders full width button", () => {
      render(
        <TestWrapper>
          <GoogleOAuthButton fullWidth />
        </TestWrapper>,
      );

      const button = screen.getByRole("button");
      expect(button).toHaveAttribute("class", expect.stringContaining("MuiButton-fullWidth"));
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

  describe("One Tap Mode", () => {
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

    it("initializes Google One Tap when script loads", async () => {
      const mockInitialize = jest.fn();
      const mockPrompt = jest.fn();

      window.google = {
        accounts: {
          id: {
            initialize: mockInitialize,
            renderButton: jest.fn(),
            prompt: mockPrompt,
          },
        },
      };

      render(
        <TestWrapper>
          <GoogleOAuthButton mode="oneTap" />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(mockInitialize).toHaveBeenCalledWith({
          client_id: "mock-client-id",
          callback: "handleGoogleCredentialResponse",
          auto_select: false,
          cancel_on_tap_outside: true,
        });
      });

      await waitFor(() => {
        expect(mockPrompt).toHaveBeenCalled();
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
      await window.handleGoogleCredentialResponse!(mockResponse);

      await waitFor(() => {
        expect(mockGoogleOAuthLogin).toHaveBeenCalledWith({
          id_token: "mock-id-token",
        });
      });

      await waitFor(() => {
        expect(onSuccess).toHaveBeenCalled();
      });
    });

    it("handles Google credential response error", async () => {
      const onError = jest.fn();
      mockGoogleOAuthLogin.mockRejectedValue({
        data: { detail: "Authentication failed" },
      });

      render(
        <TestWrapper>
          <GoogleOAuthButton mode="oneTap" onError={onError} />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(window.handleGoogleCredentialResponse).toBeDefined();
      });

      const mockResponse = { credential: "invalid-token" };
      await window.handleGoogleCredentialResponse!(mockResponse);

      await waitFor(() => {
        expect(onError).toHaveBeenCalledWith("Authentication failed");
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

      const mockResponse = {}; // No credential
      await window.handleGoogleCredentialResponse!(mockResponse);

      await waitFor(() => {
        expect(onError).toHaveBeenCalledWith("No credential received from Google");
      });
    });
  });

  describe("Redirect Mode", () => {
    it("handles redirect flow when button is clicked", async () => {
      const user = userEvent.setup();
      mockGetGoogleAuthUrl.mockResolvedValue({
        unwrap: () =>
          Promise.resolve({
            authorization_url: "https://accounts.google.com/oauth/authorize?...",
            state: "mock-state",
          }),
      });

      // Mock window.location.href
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

      await waitFor(() => {
        expect(window.location.href).toBe("https://accounts.google.com/oauth/authorize?...");
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
    it("opens popup window for OAuth flow", async () => {
      const user = userEvent.setup();
      const mockPopup = {
        closed: false,
        close: jest.fn(),
        postMessage: jest.fn(),
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

    it("handles popup success message", async () => {
      const user = userEvent.setup();
      const onSuccess = jest.fn();
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
          <GoogleOAuthButton mode="popup" onSuccess={onSuccess} />
        </TestWrapper>,
      );

      const button = screen.getByRole("button");
      await user.click(button);

      // Simulate popup success message
      const mockResult = {
        access_token: "access-token",
        refresh_token: "refresh-token",
        token_type: "Bearer",
        user: { id: 1, email: "test@example.com" },
      };

      // Trigger message event
      window.dispatchEvent(
        new MessageEvent("message", {
          data: { type: "GOOGLE_OAUTH_SUCCESS", result: mockResult },
          origin: window.location.origin,
        }),
      );

      await waitFor(() => {
        expect(mockPopup.close).toHaveBeenCalled();
        expect(onSuccess).toHaveBeenCalled();
      });
    });

    it("handles popup error message", async () => {
      const user = userEvent.setup();
      const onError = jest.fn();
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
          <GoogleOAuthButton mode="popup" onError={onError} />
        </TestWrapper>,
      );

      const button = screen.getByRole("button");
      await user.click(button);

      // Simulate popup error message
      window.dispatchEvent(
        new MessageEvent("message", {
          data: { type: "GOOGLE_OAUTH_ERROR", error: "Authentication failed" },
          origin: window.location.origin,
        }),
      );

      await waitFor(() => {
        expect(mockPopup.close).toHaveBeenCalled();
        expect(onError).toHaveBeenCalledWith("Authentication failed");
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

    it("allows dismissing error alert", async () => {
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
      });

      const closeButton = screen.getByLabelText("Close");
      await user.click(closeButton);

      await waitFor(() => {
        expect(screen.queryByRole("alert")).not.toBeInTheDocument();
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

      await waitFor(() => {
        expect(screen.queryByText("Signing in...")).not.toBeInTheDocument();
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
