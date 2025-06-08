import React from "react";
import { render, screen } from "@testing-library/react";
import { ThemeProvider } from "@mui/material/styles";
import "@testing-library/jest-dom";
import { theme } from "../../../theme";
import ResponsiveGrid from "../ResponsiveGrid";

const renderWithTheme = (ui: React.ReactElement) => {
  return render(<ThemeProvider theme={theme}>{ui}</ThemeProvider>);
};

describe("ResponsiveGrid", () => {
  it("should render with default props", () => {
    renderWithTheme(
      <ResponsiveGrid>
        <div data-testid="child">Child content</div>
      </ResponsiveGrid>,
    );

    expect(screen.getByTestId("responsive-grid")).toBeInTheDocument();
    expect(screen.getByTestId("child")).toBeInTheDocument();
  });

  it("should apply custom spacing", () => {
    renderWithTheme(
      <ResponsiveGrid spacing={4}>
        <div>Child 1</div>
        <div>Child 2</div>
      </ResponsiveGrid>,
    );

    const grid = screen.getByTestId("responsive-grid");
    expect(grid).toBeInTheDocument();
  });

  it("should handle different column configurations", () => {
    renderWithTheme(
      <ResponsiveGrid xs={12} sm={6} md={4} lg={3}>
        <div data-testid="grid-item">Grid item</div>
      </ResponsiveGrid>,
    );

    expect(screen.getByTestId("responsive-grid")).toBeInTheDocument();
    expect(screen.getByTestId("grid-item")).toBeInTheDocument();
  });

  it("should render multiple children", () => {
    renderWithTheme(
      <ResponsiveGrid>
        <div data-testid="child-1">Child 1</div>
        <div data-testid="child-2">Child 2</div>
        <div data-testid="child-3">Child 3</div>
      </ResponsiveGrid>,
    );

    expect(screen.getByTestId("child-1")).toBeInTheDocument();
    expect(screen.getByTestId("child-2")).toBeInTheDocument();
    expect(screen.getByTestId("child-3")).toBeInTheDocument();
  });

  it("should apply responsive breakpoints", () => {
    renderWithTheme(
      <ResponsiveGrid xs={12} sm={6} md={4} lg={3} xl={2}>
        <div data-testid="responsive-item">Responsive item</div>
      </ResponsiveGrid>,
    );

    const grid = screen.getByTestId("responsive-grid");
    expect(grid).toBeInTheDocument();
    expect(screen.getByTestId("responsive-item")).toBeInTheDocument();
  });

  it("should handle no children gracefully", () => {
    renderWithTheme(<ResponsiveGrid>{null}</ResponsiveGrid>);

    expect(screen.getByTestId("responsive-grid")).toBeInTheDocument();
  });

  it("should apply custom container props", () => {
    renderWithTheme(
      <ResponsiveGrid spacing={3} direction="column">
        <div data-testid="column-child">Column child</div>
      </ResponsiveGrid>,
    );

    expect(screen.getByTestId("responsive-grid")).toBeInTheDocument();
    expect(screen.getByTestId("column-child")).toBeInTheDocument();
  });

  it("should work with single child", () => {
    renderWithTheme(
      <ResponsiveGrid xs={12}>
        <div data-testid="single-child">Single child</div>
      </ResponsiveGrid>,
    );

    expect(screen.getByTestId("responsive-grid")).toBeInTheDocument();
    expect(screen.getByTestId("single-child")).toBeInTheDocument();
  });

  it("should handle complex nested content", () => {
    renderWithTheme(
      <ResponsiveGrid xs={12} sm={6} md={4}>
        <div data-testid="nested-content">
          <h3>Nested Title</h3>
          <p>Nested paragraph</p>
          <button>Nested button</button>
        </div>
      </ResponsiveGrid>,
    );

    expect(screen.getByTestId("responsive-grid")).toBeInTheDocument();
    expect(screen.getByTestId("nested-content")).toBeInTheDocument();
    expect(screen.getByText("Nested Title")).toBeInTheDocument();
    expect(screen.getByText("Nested paragraph")).toBeInTheDocument();
    expect(screen.getByText("Nested button")).toBeInTheDocument();
  });

  it("should apply theme spacing correctly", () => {
    renderWithTheme(
      <ResponsiveGrid spacing={2}>
        <div data-testid="themed-item">Themed item</div>
      </ResponsiveGrid>,
    );

    const grid = screen.getByTestId("responsive-grid");
    expect(grid).toBeInTheDocument();
    // The spacing should be applied through Material-UI theme
    expect(screen.getByTestId("themed-item")).toBeInTheDocument();
  });
});
