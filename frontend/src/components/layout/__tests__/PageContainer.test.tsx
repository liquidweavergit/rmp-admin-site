import React from "react";
import { render, screen } from "@testing-library/react";
import { ThemeProvider } from "@mui/material/styles";
import "@testing-library/jest-dom";
import { theme } from "../../../theme";
import PageContainer from "../PageContainer";

const renderWithTheme = (ui: React.ReactElement) => {
  return render(<ThemeProvider theme={theme}>{ui}</ThemeProvider>);
};

describe("PageContainer", () => {
  it("should render with title and children", () => {
    renderWithTheme(
      <PageContainer title="Test Page">
        <div data-testid="page-content">Page content</div>
      </PageContainer>,
    );

    expect(screen.getByTestId("page-container")).toBeInTheDocument();
    expect(screen.getByTestId("page-title")).toHaveTextContent("Test Page");
    expect(screen.getByTestId("page-content")).toBeInTheDocument();
    expect(screen.getByTestId("page-content-wrapper")).toBeInTheDocument();
  });

  it("should render with optional subtitle", () => {
    renderWithTheme(
      <PageContainer title="Test Page" subtitle="Test subtitle">
        <div>Content</div>
      </PageContainer>,
    );

    expect(screen.getByTestId("page-subtitle")).toHaveTextContent("Test subtitle");
  });

  it("should render with breadcrumbs when provided", () => {
    const breadcrumbs = [
      { label: "Home", href: "/" },
      { label: "Section", href: "/section" },
      { label: "Current Page" },
    ];

    renderWithTheme(
      <PageContainer title="Test Page" breadcrumbs={breadcrumbs}>
        <div>Content</div>
      </PageContainer>,
    );

    expect(screen.getByTestId("page-breadcrumbs")).toBeInTheDocument();
    expect(screen.getByText("Home")).toBeInTheDocument();
    expect(screen.getByText("Section")).toBeInTheDocument();
    expect(screen.getByText("Current Page")).toBeInTheDocument();
  });

  it("should render with action buttons when provided", () => {
    const actions = <button data-testid="action-button">Action</button>;

    renderWithTheme(
      <PageContainer title="Test Page" actions={actions}>
        <div>Content</div>
      </PageContainer>,
    );

    expect(screen.getByTestId("page-actions")).toBeInTheDocument();
    expect(screen.getByTestId("action-button")).toBeInTheDocument();
  });

  it("should have responsive padding", () => {
    renderWithTheme(
      <PageContainer title="Test Page">
        <div>Content</div>
      </PageContainer>,
    );

    const container = screen.getByTestId("page-container");
    expect(container).toHaveStyle({
      padding: expect.any(String),
    });
  });

  it("should render loading state", () => {
    renderWithTheme(
      <PageContainer title="Test Page" loading>
        <div>Content</div>
      </PageContainer>,
    );

    expect(screen.getByTestId("page-loading")).toBeInTheDocument();
  });
});
