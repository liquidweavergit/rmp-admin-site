import React from "react";
import { Typography, Box, Paper, Grid, Chip } from "@mui/material";
import { useGetHealthQuery } from "../store";
import { PageContainer } from "../components/layout";

const Home: React.FC = () => {
  const { data: healthData, isLoading, error } = useGetHealthQuery();

  return (
    <PageContainer
      title="Dashboard"
      subtitle="Welcome to the Men's Circle Management Platform"
      loading={isLoading}
    >
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 3, height: "100%" }}>
            <Typography variant="h6" gutterBottom>
              System Status
            </Typography>

            {error && (
              <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                <Chip label="Offline" color="error" size="small" />
                <Typography color="error" variant="body2">
                  Error connecting to backend
                </Typography>
              </Box>
            )}

            {healthData && (
              <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                <Chip label="Online" color="success" size="small" />
                <Typography color="success.main" variant="body2">
                  Backend Status: {healthData.status}
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 3, height: "100%" }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Navigation and quick actions will be available here once authentication is
              implemented.
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Development Environment
            </Typography>
            <Typography variant="body1" paragraph>
              The development environment has been successfully configured with responsive layout
              components:
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Chip label="React 18 + TypeScript" variant="outlined" />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Chip label="Material-UI Components" variant="outlined" />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Chip label="Redux Toolkit" variant="outlined" />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Chip label="Responsive Layout" variant="outlined" />
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </PageContainer>
  );
};

export default Home;
