import React from 'react';
import { Container, Typography, Box, Paper } from '@mui/material';
import { useGetHealthQuery } from '../store';

const Home: React.FC = () => {
  const { data: healthData, isLoading, error } = useGetHealthQuery();

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h2" component="h1" gutterBottom>
          Men's Circle Management Platform
        </Typography>
        
        <Paper elevation={3} sx={{ p: 3, mt: 3 }}>
          <Typography variant="h5" gutterBottom>
            System Status
          </Typography>
          
          {isLoading && <Typography>Checking system health...</Typography>}
          
          {error && (
            <Typography color="error">
              Error connecting to backend
            </Typography>
          )}
          
          {healthData && (
            <Box>
              <Typography color="success.main">
                ✅ Backend Status: {healthData.status}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Service: {healthData.service || 'Unknown'}
              </Typography>
            </Box>
          )}
        </Paper>
        
        <Paper elevation={3} sx={{ p: 3, mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            Development Environment Setup Complete
          </Typography>
          <Typography variant="body1">
            This is the Men's Circle Management Platform frontend. 
            The development environment has been successfully configured with:
          </Typography>
          <Box component="ul" sx={{ mt: 2 }}>
            <li>React 18 with TypeScript</li>
            <li>Material-UI for components</li>
            <li>Redux Toolkit for state management</li>
            <li>React Router for navigation</li>
            <li>RTK Query for API integration</li>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default Home; 