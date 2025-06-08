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
  Group as GroupIcon,
  Event as EventIcon,
  Assignment as AssignmentIcon,
  Analytics as AnalyticsIcon,
} from "@mui/icons-material";

const FacilitatorPanel: React.FC = () => {
  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        Facilitator Dashboard
      </Typography>

      <Typography variant="body1" color="text.secondary" paragraph>
        Manage your circles and facilitate meaningful connections.
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Circle Management
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <GroupIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="My Circles"
                    secondary="View and manage your facilitated circles"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <AssignmentIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Member Management"
                    secondary="Add, remove, and manage circle members"
                  />
                </ListItem>
              </List>
              <Button variant="contained" color="primary" sx={{ mt: 2 }}>
                Manage Circles
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Meeting Tools
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <EventIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Schedule Meetings"
                    secondary="Plan and schedule circle meetings"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <AnalyticsIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Attendance Tracking"
                    secondary="Record and track member attendance"
                  />
                </ListItem>
              </List>
              <Button variant="contained" color="primary" sx={{ mt: 2 }}>
                Meeting Tools
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default FacilitatorPanel;
