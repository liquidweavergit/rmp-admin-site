import React from "react";
import { Grid, GridProps, useTheme, useMediaQuery } from "@mui/material";

interface ResponsiveGridProps {
  children: React.ReactNode;
  spacing?: number;
  container?: boolean;
  item?: boolean;
  xs?: GridProps["xs"];
  sm?: GridProps["sm"];
  md?: GridProps["md"];
  lg?: GridProps["lg"];
  xl?: GridProps["xl"];
  direction?: "row" | "column";
  justifyContent?:
    | "flex-start"
    | "center"
    | "flex-end"
    | "space-between"
    | "space-around"
    | "space-evenly";
  alignItems?: "flex-start" | "center" | "flex-end" | "stretch" | "baseline";
}

const ResponsiveGrid: React.FC<ResponsiveGridProps> = ({
  children,
  spacing = 2,
  container = true,
  item = false,
  xs = 12,
  sm,
  md,
  lg,
  xl,
  direction = "row",
  justifyContent,
  alignItems,
  ...props
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  // Auto-adjust spacing for mobile
  const responsiveSpacing = isMobile ? Math.min(spacing, 2) : spacing;

  return (
    <Grid
      data-testid="responsive-grid"
      container={container}
      item={item}
      spacing={responsiveSpacing}
      direction={direction}
      justifyContent={justifyContent}
      alignItems={alignItems}
      xs={xs}
      sm={sm}
      md={md}
      lg={lg}
      xl={xl}
      sx={{
        width: "100%",
        margin: 0,
        "& .MuiGrid-item": {
          paddingLeft: theme.spacing(responsiveSpacing / 2),
          paddingTop: theme.spacing(responsiveSpacing / 2),
        },
      }}
      {...props}
    >
      {children}
    </Grid>
  );
};

export default ResponsiveGrid;
