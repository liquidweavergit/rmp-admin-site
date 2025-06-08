import React from "react";
import { render, screen } from "@testing-library/react";
import { Provider } from "react-redux";
import { ThemeProvider } from "@mui/material/styles";
import "@testing-library/jest-dom";
import Home from "../Home";
import { store } from "../../store";
import { theme } from "../../theme";

// Mock the layout components
jest.mock("../../components/layout", () => ({
  PageContainer: ({ title, subtitle, children }: any) => (
    <div data-testid="page-container">
      <h1 data-testid="page-title">{title}</h1>
      {subtitle && <p data-testid="page-subtitle">{subtitle}</p>}
      <div data-testid="page-content">{children}</div>
    </div>
  ),
}));

// Mock the API query hook
jest.mock("../../store", () => ({
  store: {
    getState: () => ({}),
    dispatch: jest.fn(),
    subscribe: jest.fn(),
  },
  useGetHealthQuery: () => ({
    data: null,
    isLoading: false,
    error: { message: "Connection failed" },
  }),
}));

const renderWithProviders = (ui: React.ReactElement) => {
  return render(
    <Provider store={store}>
      <ThemeProvider theme={theme}>{ui}</ThemeProvider>
    </Provider>,
  );
};

describe("Home", () => {
  it("should render the dashboard with correct title", () => {
    renderWithProviders(<Home />);

    expect(screen.getByTestId("page-container")).toBeInTheDocument();
    expect(screen.getByTestId("page-title")).toHaveTextContent("Dashboard");
  });

  it("should render the subtitle", () => {
    renderWithProviders(<Home />);

    expect(screen.getByTestId("page-subtitle")).toHaveTextContent(
      "Welcome to the Men's Circle Management Platform",
    );
  });

  it("should render system status section", () => {
    renderWithProviders(<Home />);

    expect(screen.getByText("System Status")).toBeInTheDocument();
    expect(screen.getByText("Offline")).toBeInTheDocument();
    expect(screen.getByText("Error connecting to backend")).toBeInTheDocument();
  });

  it("should render quick actions section", () => {
    renderWithProviders(<Home />);

    expect(screen.getByText("Quick Actions")).toBeInTheDocument();
    expect(screen.getByText(/Navigation and quick actions will be available/)).toBeInTheDocument();
  });

  it("should render development environment section", () => {
    renderWithProviders(<Home />);

    expect(screen.getByText("Development Environment")).toBeInTheDocument();
    expect(
      screen.getByText(/The development environment has been successfully configured/),
    ).toBeInTheDocument();
  });

  it("should render technology stack chips", () => {
    renderWithProviders(<Home />);

    expect(screen.getByText("React 18 + TypeScript")).toBeInTheDocument();
    expect(screen.getByText("Material-UI Components")).toBeInTheDocument();
    expect(screen.getByText("Redux Toolkit")).toBeInTheDocument();
    expect(screen.getByText("Responsive Layout")).toBeInTheDocument();
  });

  it("should have proper grid layout", () => {
    renderWithProviders(<Home />);

    // Should render the main sections in a grid layout
    const systemStatus = screen.getByText("System Status");
    const quickActions = screen.getByText("Quick Actions");
    const devEnvironment = screen.getByText("Development Environment");

    expect(systemStatus).toBeInTheDocument();
    expect(quickActions).toBeInTheDocument();
    expect(devEnvironment).toBeInTheDocument();
  });

  it("should show offline status when backend connection fails", () => {
    renderWithProviders(<Home />);

    expect(screen.getByText("Offline")).toBeInTheDocument();
    expect(screen.getByText("Error connecting to backend")).toBeInTheDocument();
  });

  it("should display technology stack information", () => {
    renderWithProviders(<Home />);

    // Check for all four technology chips
    const techChips = [
      "React 18 + TypeScript",
      "Material-UI Components",
      "Redux Toolkit",
      "Responsive Layout",
    ];

    techChips.forEach((chip) => {
      expect(screen.getByText(chip)).toBeInTheDocument();
    });
  });
});
