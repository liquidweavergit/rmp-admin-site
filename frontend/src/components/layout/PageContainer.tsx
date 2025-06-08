import React from "react";
import {
  Box,
  Typography,
  Breadcrumbs,
  Link,
  CircularProgress,
  Stack,
  useTheme,
  useMediaQuery,
} from "@mui/material";
import NavigateNextIcon from "@mui/icons-material/NavigateNext";

interface BreadcrumbItem {
  label: string;
  href?: string;
}

interface PageContainerProps {
  title: string;
  subtitle?: string;
  breadcrumbs?: BreadcrumbItem[];
  actions?: React.ReactNode;
  loading?: boolean;
  children: React.ReactNode;
}

const PageContainer: React.FC<PageContainerProps> = ({
  title,
  subtitle,
  breadcrumbs,
  actions,
  loading,
  children,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  return (
    <Box
      data-testid="page-container"
      sx={{
        p: { xs: 2, sm: 3, md: 4 },
        minHeight: "100%",
        backgroundColor: theme.palette.background.default,
      }}
    >
      {/* Breadcrumbs */}
      {breadcrumbs && breadcrumbs.length > 0 && (
        <Breadcrumbs
          data-testid="page-breadcrumbs"
          separator={<NavigateNextIcon fontSize="small" />}
          sx={{ mb: 2 }}
        >
          {breadcrumbs.map((breadcrumb, index) =>
            breadcrumb.href ? (
              <Link
                key={index}
                underline="hover"
                color="inherit"
                href={breadcrumb.href}
                sx={{
                  fontSize: { xs: "0.875rem", sm: "1rem" },
                }}
              >
                {breadcrumb.label}
              </Link>
            ) : (
              <Typography
                key={index}
                color="text.primary"
                sx={{
                  fontSize: { xs: "0.875rem", sm: "1rem" },
                }}
              >
                {breadcrumb.label}
              </Typography>
            ),
          )}
        </Breadcrumbs>
      )}

      {/* Page Header */}
      <Box
        sx={{
          display: "flex",
          flexDirection: { xs: "column", sm: "row" },
          justifyContent: "space-between",
          alignItems: { xs: "flex-start", sm: "center" },
          mb: 3,
          gap: { xs: 2, sm: 0 },
        }}
      >
        <Box>
          <Typography
            data-testid="page-title"
            variant={isMobile ? "h4" : "h3"}
            component="h1"
            sx={{
              fontWeight: 600,
              color: theme.palette.text.primary,
              mb: subtitle ? 1 : 0,
            }}
          >
            {title}
          </Typography>
          {subtitle && (
            <Typography
              data-testid="page-subtitle"
              variant="subtitle1"
              color="text.secondary"
              sx={{
                fontSize: { xs: "1rem", sm: "1.125rem" },
              }}
            >
              {subtitle}
            </Typography>
          )}
        </Box>

        {actions && (
          <Box data-testid="page-actions" sx={{ flexShrink: 0 }}>
            {actions}
          </Box>
        )}
      </Box>

      {/* Loading State */}
      {loading && (
        <Box
          data-testid="page-loading"
          sx={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            minHeight: 200,
          }}
        >
          <Stack spacing={2} alignItems="center">
            <CircularProgress />
            <Typography variant="body2" color="text.secondary">
              Loading...
            </Typography>
          </Stack>
        </Box>
      )}

      {/* Page Content */}
      {!loading && (
        <Box
          data-testid="page-content"
          sx={{
            backgroundColor: theme.palette.background.paper,
            borderRadius: 1,
            p: { xs: 2, sm: 3 },
            boxShadow: theme.shadows[1],
          }}
        >
          {children}
        </Box>
      )}
    </Box>
  );
};

export default PageContainer;
