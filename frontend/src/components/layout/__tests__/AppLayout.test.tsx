import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { ThemeProvider } from "@mui/material/styles";
import { BrowserRouter } from "react-router-dom";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import "@testing-library/jest-dom";
import { theme } from "../../../theme";
import AppLayout from "../AppLayout";

// Mock store for testing
const mockStore = configureStore({
  reducer: {
    // Add mock reducers as needed
  },
});

const renderWithProviders = (ui: React.ReactElement) => {
  return render(
    <Provider store={mockStore}>
      <ThemeProvider theme={theme}>
        <BrowserRouter>{ui}</BrowserRouter>
      </ThemeProvider>
    </Provider>,
  );
};

describe("AppLayout", () => {
  it("should render the main layout structure", () => {
    renderWithProviders(
      <AppLayout>
        <div data-testid="content">Test Content</div>
      </AppLayout>,
    );

    expect(screen.getByTestId("app-layout")).toBeInTheDocument();
    expect(screen.getByTestId("content")).toBeInTheDocument();
  });

  it("should have responsive navigation header", () => {
    renderWithProviders(
      <AppLayout>
        <div>Content</div>
      </AppLayout>,
    );

    expect(screen.getByTestId("app-header")).toBeInTheDocument();
    expect(screen.getByTestId("app-title")).toHaveTextContent("Men's Circle Platform");
  });

  it("should show mobile menu button on small screens", () => {
    // Mock window.matchMedia for mobile viewport
    Object.defineProperty(window, "matchMedia", {
      writable: true,
      value: jest.fn().mockImplementation((query) => ({
        matches: query === "(max-width: 768px)",
        media: query,
        onchange: null,
        addListener: jest.fn(),
        removeListener: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
      })),
    });

    renderWithProviders(
      <AppLayout>
        <div>Content</div>
      </AppLayout>,
    );

    expect(screen.getByTestId("mobile-menu-button")).toBeInTheDocument();
  });

  it("should toggle mobile drawer when menu button clicked", () => {
    renderWithProviders(
      <AppLayout>
        <div>Content</div>
      </AppLayout>,
    );

    const menuButton = screen.getByTestId("mobile-menu-button");
    fireEvent.click(menuButton);

    expect(screen.getByTestId("mobile-drawer")).toHaveAttribute("aria-hidden", "false");
  });

  it("should have responsive main content area", () => {
    renderWithProviders(
      <AppLayout>
        <div data-testid="test-content">Test Content</div>
      </AppLayout>,
    );

    const mainContent = screen.getByTestId("main-content");
    expect(mainContent).toBeInTheDocument();
    expect(screen.getByTestId("test-content")).toBeInTheDocument();
  });

  it("should show navigation items in header on desktop", () => {
    // Mock desktop viewport
    Object.defineProperty(window, "matchMedia", {
      writable: true,
      value: jest.fn().mockImplementation((query) => ({
        matches: query !== "(max-width: 768px)",
        media: query,
        onchange: null,
        addListener: jest.fn(),
        removeListener: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
      })),
    });

    renderWithProviders(
      <AppLayout>
        <div>Content</div>
      </AppLayout>,
    );

    expect(screen.getByTestId("desktop-navigation")).toBeInTheDocument();
  });
});
