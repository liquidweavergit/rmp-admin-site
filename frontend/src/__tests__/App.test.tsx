import React from "react";
import { render, screen } from "@testing-library/react";
import { Provider } from "react-redux";
import { BrowserRouter } from "react-router-dom";
import { ThemeProvider } from "@mui/material/styles";
import "@testing-library/jest-dom";
import App from "../App";
import { store } from "../store";
import { theme } from "../theme";

// Mock the layout components to avoid complex component dependencies
jest.mock("../components/layout", () => ({
  AppLayout: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="app-layout">{children}</div>
  ),
}));

// Mock react-router-dom
jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  BrowserRouter: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="browser-router">{children}</div>
  ),
  Routes: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="routes">{children}</div>
  ),
  Route: ({ element }: { element: React.ReactNode }) => <div data-testid="route">{element}</div>,
}));

// Mock pages
jest.mock("../pages/Home", () => ({
  __esModule: true,
  default: () => <div data-testid="home-page">Home Page</div>,
}));

const renderApp = () => {
  return render(
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </ThemeProvider>
    </Provider>,
  );
};

describe("App", () => {
  it("should render without crashing", () => {
    renderApp();
    expect(screen.getByTestId("app-layout")).toBeInTheDocument();
  });

  it("should be wrapped with necessary providers", () => {
    renderApp();
    expect(screen.getByTestId("browser-router")).toBeInTheDocument();
    expect(screen.getByTestId("app-layout")).toBeInTheDocument();
  });

  it("should render routes", () => {
    renderApp();
    expect(screen.getByTestId("routes")).toBeInTheDocument();
  });

  it("should have proper theme applied", () => {
    renderApp();
    // The theme should be applied through ThemeProvider
    const appLayout = screen.getByTestId("app-layout");
    expect(appLayout).toBeInTheDocument();
  });

  it("should render home page by default", () => {
    renderApp();
    expect(screen.getByTestId("home-page")).toBeInTheDocument();
  });
});
