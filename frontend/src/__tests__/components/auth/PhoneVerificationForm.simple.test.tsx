import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import { ThemeProvider } from "@mui/material/styles";
import "@testing-library/jest-dom";

import { PhoneVerificationForm } from "../../../components/auth/PhoneVerificationForm";
import { api } from "../../../store";
import { theme } from "../../../theme";

// Mock validation utility
jest.mock("../../../utils/validation", () => ({
  validatePhone: jest.fn((phone: string) => {
    if (!phone) {
      return { isValid: false, errors: ["Phone number is required"] };
    }
    if (phone === "invalid") {
      return { isValid: false, errors: ["Invalid phone number format"] };
    }
    return { isValid: true, errors: [] };
  }),
}));

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

const renderPhoneVerificationForm = (props = {}) => {
  const store = createMockStore();
  const user = userEvent.setup();

  const defaultProps = {
    onSuccess: jest.fn(),
    onSkip: jest.fn(),
    showTitle: true,
    allowSkip: true,
  };

  const utils = render(
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        <PhoneVerificationForm {...defaultProps} {...props} />
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

describe("PhoneVerificationForm - Core Functionality", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("Rendering", () => {
    it("should render all essential form elements", () => {
      renderPhoneVerificationForm();

      // Check for phone input
      expect(screen.getByRole("textbox", { name: /phone number/i })).toBeInTheDocument();

      // Check for send verification code button
      expect(screen.getByRole("button", { name: /send verification code/i })).toBeInTheDocument();

      // Check for stepper
      expect(screen.getByText("Enter Phone Number")).toBeInTheDocument();
      expect(screen.getByText("Verify Code")).toBeInTheDocument();
      expect(screen.getByText("Complete")).toBeInTheDocument();
    });

    it("should render title when showTitle is true", () => {
      renderPhoneVerificationForm({ showTitle: true });
      expect(screen.getByRole("heading", { name: /verify phone number/i })).toBeInTheDocument();
    });

    it("should not render title when showTitle is false", () => {
      renderPhoneVerificationForm({ showTitle: false });
      expect(
        screen.queryByRole("heading", { name: /verify phone number/i }),
      ).not.toBeInTheDocument();
    });

    it("should render skip button when allowSkip is true", () => {
      renderPhoneVerificationForm({ allowSkip: true });
      expect(screen.getByRole("button", { name: /skip for now/i })).toBeInTheDocument();
    });

    it("should not render skip button when allowSkip is false", () => {
      renderPhoneVerificationForm({ allowSkip: false });
      expect(screen.queryByRole("button", { name: /skip for now/i })).not.toBeInTheDocument();
    });

    it("should pre-fill phone number when initialPhone is provided", () => {
      renderPhoneVerificationForm({ initialPhone: "+1234567890" });
      const phoneInput = screen.getByRole("textbox", { name: /phone number/i });
      expect(phoneInput).toHaveValue("+1234567890");
    });
  });

  describe("Form Interaction", () => {
    it("should allow typing in phone number field", async () => {
      const { user } = renderPhoneVerificationForm();
      const phoneInput = screen.getByRole("textbox", { name: /phone number/i });

      await user.type(phoneInput, "+1234567890");
      expect(phoneInput).toHaveValue("+1234567890");
    });

    it("should disable send button when phone is empty", () => {
      renderPhoneVerificationForm();
      const sendButton = screen.getByRole("button", { name: /send verification code/i });
      expect(sendButton).toBeDisabled();
    });

    it("should enable send button when phone is provided", async () => {
      const { user } = renderPhoneVerificationForm();
      const phoneInput = screen.getByRole("textbox", { name: /phone number/i });

      await user.type(phoneInput, "+1234567890");

      const sendButton = screen.getByRole("button", { name: /send verification code/i });
      expect(sendButton).not.toBeDisabled();
    });

    it("should call onSkip when skip button is clicked", async () => {
      const { user, props } = renderPhoneVerificationForm();
      const skipButton = screen.getByRole("button", { name: /skip for now/i });

      await user.click(skipButton);
      expect(props.onSkip).toHaveBeenCalledTimes(1);
    });
  });

  describe("Form Validation", () => {
    it("should show validation error for invalid phone number", async () => {
      const { user } = renderPhoneVerificationForm();
      const phoneInput = screen.getByRole("textbox", { name: /phone number/i });
      const sendButton = screen.getByRole("button", { name: /send verification code/i });

      await user.type(phoneInput, "invalid");
      await user.click(sendButton);

      await waitFor(() => {
        expect(screen.getByText(/invalid phone number format/i)).toBeInTheDocument();
      });
    });

    it("should clear validation error when user corrects input", async () => {
      const { user } = renderPhoneVerificationForm();
      const phoneInput = screen.getByRole("textbox", { name: /phone number/i });
      const sendButton = screen.getByRole("button", { name: /send verification code/i });

      // First enter invalid phone
      await user.type(phoneInput, "invalid");
      await user.click(sendButton);

      await waitFor(() => {
        expect(screen.getByText(/invalid phone number format/i)).toBeInTheDocument();
      });

      // Clear the input and enter valid phone
      await user.clear(phoneInput);
      await user.type(phoneInput, "+1234567890");

      await waitFor(() => {
        expect(screen.queryByText(/invalid phone number format/i)).not.toBeInTheDocument();
      });
    });
  });

  describe("User Experience", () => {
    it("should display helpful placeholder text", () => {
      renderPhoneVerificationForm();
      expect(screen.getByText(/format: \+1 \(555\) 123-4567 or 5551234567/i)).toBeInTheDocument();
    });

    it("should display instructions for phone entry", () => {
      renderPhoneVerificationForm();
      expect(
        screen.getByText(/enter your phone number to receive a verification code via sms/i),
      ).toBeInTheDocument();
    });
  });

  describe("Accessibility", () => {
    it("should have proper form labels and attributes", () => {
      renderPhoneVerificationForm();

      const phoneInput = screen.getByRole("textbox", { name: /phone number/i });
      expect(phoneInput).toHaveAttribute("type", "tel");
      expect(phoneInput).toHaveAttribute("autoComplete", "tel");
    });

    it("should have proper heading structure when title is shown", () => {
      renderPhoneVerificationForm({ showTitle: true });
      const heading = screen.getByRole("heading", { name: /verify phone number/i });
      expect(heading.tagName).toBe("H1");
    });

    it("should have proper button roles", () => {
      renderPhoneVerificationForm();

      expect(screen.getByRole("button", { name: /send verification code/i })).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /skip for now/i })).toBeInTheDocument();
    });
  });

  describe("State Management", () => {
    it("should start at step 0 (phone entry)", () => {
      renderPhoneVerificationForm();

      // First step should be active
      expect(
        screen.getByText(/enter your phone number to receive a verification code/i),
      ).toBeInTheDocument();
      expect(screen.getByRole("textbox", { name: /phone number/i })).toBeInTheDocument();
    });

    it("should maintain phone number state across interactions", async () => {
      const { user } = renderPhoneVerificationForm();
      const phoneInput = screen.getByRole("textbox", { name: /phone number/i });

      await user.type(phoneInput, "+1234567890");
      expect(phoneInput).toHaveValue("+1234567890");

      // Type more characters
      await user.type(phoneInput, "123");
      expect(phoneInput).toHaveValue("+1234567890123");
    });
  });
});

// Basic phone validation tests
describe("PhoneVerificationForm - Validation Logic", () => {
  it("should use validation utility correctly", async () => {
    const { validatePhone } = require("../../../utils/validation");
    const { user } = renderPhoneVerificationForm();

    const phoneInput = screen.getByRole("textbox", { name: /phone number/i });
    const sendButton = screen.getByRole("button", { name: /send verification code/i });

    await user.type(phoneInput, "+1234567890");
    await user.click(sendButton);

    expect(validatePhone).toHaveBeenCalledWith("+1234567890");
  });

  it("should handle validation utility errors correctly", async () => {
    const { user } = renderPhoneVerificationForm();

    const phoneInput = screen.getByRole("textbox", { name: /phone number/i });
    const sendButton = screen.getByRole("button", { name: /send verification code/i });

    await user.type(phoneInput, "invalid");
    await user.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(/invalid phone number format/i)).toBeInTheDocument();
    });
  });
});

// Component props and configuration tests
describe("PhoneVerificationForm - Configuration", () => {
  it("should respect initialPhone prop", () => {
    const testPhone = "+19876543210";
    renderPhoneVerificationForm({ initialPhone: testPhone });

    const phoneInput = screen.getByRole("textbox", { name: /phone number/i });
    expect(phoneInput).toHaveValue(testPhone);
  });

  it("should respect showTitle prop", () => {
    const { rerender } = renderPhoneVerificationForm({ showTitle: true });
    expect(screen.getByRole("heading", { name: /verify phone number/i })).toBeInTheDocument();

    rerender(
      <Provider store={createMockStore()}>
        <ThemeProvider theme={theme}>
          <PhoneVerificationForm showTitle={false} onSuccess={jest.fn()} onSkip={jest.fn()} />
        </ThemeProvider>
      </Provider>,
    );
    expect(screen.queryByRole("heading", { name: /verify phone number/i })).not.toBeInTheDocument();
  });

  it("should respect allowSkip prop", () => {
    const { rerender } = renderPhoneVerificationForm({ allowSkip: true });
    expect(screen.getByRole("button", { name: /skip for now/i })).toBeInTheDocument();

    rerender(
      <Provider store={createMockStore()}>
        <ThemeProvider theme={theme}>
          <PhoneVerificationForm allowSkip={false} onSuccess={jest.fn()} onSkip={jest.fn()} />
        </ThemeProvider>
      </Provider>,
    );
    expect(screen.queryByRole("button", { name: /skip for now/i })).not.toBeInTheDocument();
  });
});
