import React from "react";
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Alert,
} from "@mui/material";
import { useSelector } from "react-redux";
import { RootState, useGetUserProfileQuery } from "../store";
import {
  hasRole,
  canManageCircles,
  canManageEvents,
  canManageUsers,
  isSystemAdmin,
  getPrimaryRole,
} from "../utils/permissions";

const Dashboard: React.FC = () => {
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);
  const { data: userProfile, isLoading } = useGetUserProfileQuery(undefined, {
    skip: !isAuthenticated,
  });

  if (isLoading) {
    return (
      <Box p={3}>
        <Typography>Loading dashboard...</Typography>
      </Box>
    );
  }

  if (!userProfile) {
    return (
      <Box p={3}>
        <Alert severity="error">Unable to load user profile</Alert>
      </Box>
    );
  }

  const primaryRole = getPrimaryRole(userProfile);
  const userRoles = userProfile.roles.map((ur) => ur.role.name);

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      <Typography variant="h6" gutterBottom>
        Welcome, {userProfile.first_name} {userProfile.last_name}
      </Typography>

      {/* User Role Information */}
      <Box mb={3}>
        <Typography variant="subtitle1" gutterBottom>
          Your Roles:
        </Typography>
        <Box display="flex" gap={1} flexWrap="wrap">
          {userProfile.roles.map((userRole) => (
            <Chip
              key={userRole.role.id}
              label={userRole.role.name}
              color={userRole.is_primary ? "primary" : "default"}
              variant={userRole.is_primary ? "filled" : "outlined"}
            />
          ))}
        </Box>
        {primaryRole && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Primary Role: {primaryRole.name}
          </Typography>
        )}
      </Box>

      {/* Role-based Dashboard Content */}
      <Grid container spacing={3}>
        {/* Member Dashboard */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Member Features
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Available to all members
              </Typography>
            </CardContent>
            <CardActions>
              <Button size="small">View My Circles</Button>
              <Button size="small">Browse Events</Button>
            </CardActions>
          </Card>
        </Grid>

        {/* Facilitator Dashboard */}
        {(hasRole(userProfile, "Facilitator") || canManageCircles(userProfile)) && (
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Facilitator Tools
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Circle management and facilitation tools
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small" color="primary">
                  Manage Circles
                </Button>
                <Button size="small">Schedule Meetings</Button>
              </CardActions>
            </Card>
          </Grid>
        )}

        {/* PTM Dashboard */}
        {(hasRole(userProfile, "PTM") || canManageEvents(userProfile)) && (
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Production Team Manager
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Event production and logistics management
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small" color="primary">
                  Manage Events
                </Button>
                <Button size="small">Staff Assignments</Button>
              </CardActions>
            </Card>
          </Grid>
        )}

        {/* Manager Dashboard */}
        {hasRole(userProfile, "Manager") && (
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Manager Tools
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Team and resource management
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small" color="primary">
                  Team Management
                </Button>
                <Button size="small">Reports</Button>
              </CardActions>
            </Card>
          </Grid>
        )}

        {/* Director Dashboard */}
        {hasRole(userProfile, "Director") && (
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Director Dashboard
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Strategic oversight and operations
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small" color="primary">
                  Strategic View
                </Button>
                <Button size="small">Financial Reports</Button>
              </CardActions>
            </Card>
          </Grid>
        )}

        {/* Admin Dashboard */}
        {(hasRole(userProfile, "Admin") || isSystemAdmin(userProfile)) && (
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  System Administration
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  User management and system configuration
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small" color="primary">
                  User Management
                </Button>
                <Button size="small">System Settings</Button>
              </CardActions>
            </Card>
          </Grid>
        )}
      </Grid>

      {/* Permissions Debug Info (for development) */}
      {process.env.NODE_ENV === "development" && (
        <Box mt={4}>
          <Typography variant="h6" gutterBottom>
            Debug: User Permissions
          </Typography>
          <Box
            component="pre"
            sx={{
              backgroundColor: "grey.100",
              p: 2,
              borderRadius: 1,
              fontSize: "0.75rem",
              overflow: "auto",
            }}
          >
            {JSON.stringify(
              {
                roles: userRoles,
                permissions: userProfile.permissions,
                canManageCircles: canManageCircles(userProfile),
                canManageEvents: canManageEvents(userProfile),
                canManageUsers: canManageUsers(userProfile),
                isSystemAdmin: isSystemAdmin(userProfile),
              },
              null,
              2,
            )}
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default Dashboard;
