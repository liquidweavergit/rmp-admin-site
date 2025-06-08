import React from "react";
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from "@mui/material";
import {
  People as PeopleIcon,
  Settings as SettingsIcon,
  Security as SecurityIcon,
  Storage as StorageIcon,
} from "@mui/icons-material";

const AdminPanel: React.FC = () => {
  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        System Administration
      </Typography>

      <Typography variant="body1" color="text.secondary" paragraph>
        Welcome to the admin panel. You have full system administration privileges.
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                User Management
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <PeopleIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Manage Users"
                    secondary="Create, edit, and delete user accounts"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <SecurityIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Role Assignment"
                    secondary="Assign and manage user roles"
                  />
                </ListItem>
              </List>
              <Button variant="contained" color="primary" sx={{ mt: 2 }}>
                Manage Users
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Configuration
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <SettingsIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="System Settings"
                    secondary="Configure application settings"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <StorageIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Database Management"
                    secondary="Backup and maintenance operations"
                  />
                </ListItem>
              </List>
              <Button variant="contained" color="primary" sx={{ mt: 2 }}>
                System Settings
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AdminPanel;
