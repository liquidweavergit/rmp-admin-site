import React from "react";
import { render, screen } from "@testing-library/react";
import { ThemeProvider } from "@mui/material/styles";
import { BrowserRouter } from "react-router-dom";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import "@testing-library/jest-dom";
import { theme } from "../../../theme";
import { AppLayout, PageContainer } from "../index";

// Mock store for testing
const mockStore = configureStore({
  reducer: {
    api: () => ({}),
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

describe("Responsive Layout Integration", () => {
  it("should render AppLayout with PageContainer", () => {
    renderWithProviders(
      <AppLayout>
        <PageContainer title="Test Page">
          <div data-testid="test-content">Test content</div>
        </PageContainer>
      </AppLayout>,
    );

    expect(screen.getByTestId("app-layout")).toBeInTheDocument();
    expect(screen.getByTestId("page-container")).toBeInTheDocument();
    expect(screen.getByTestId("test-content")).toBeInTheDocument();
    expect(screen.getByText("Test Page")).toBeInTheDocument();
  });

  it("should have responsive navigation", () => {
    renderWithProviders(
      <AppLayout>
        <PageContainer title="Test Page">
          <div>Content</div>
        </PageContainer>
      </AppLayout>,
    );

    expect(screen.getByTestId("app-header")).toBeInTheDocument();
    expect(screen.getByText("Men's Circle Platform")).toBeInTheDocument();
  });

  it("should render page content within layout", () => {
    renderWithProviders(
      <AppLayout>
        <PageContainer title="Dashboard" subtitle="Welcome">
          <div data-testid="dashboard-content">Dashboard content</div>
        </PageContainer>
      </AppLayout>,
    );

    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Welcome")).toBeInTheDocument();
    expect(screen.getByTestId("dashboard-content")).toBeInTheDocument();
  });
});
