import React from "react";
import { Container, Box, Typography } from "@mui/material";
import { useNavigate, useLocation } from "react-router-dom";
import { LoginForm } from "../components/auth";

export const Login: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  // Get the intended destination from location state, default to home
  const from = (location.state as any)?.from?.pathname || "/";

  const handleLoginSuccess = () => {
    // Redirect to intended destination or home
    navigate(from, { replace: true });
  };

  const handleSwitchToRegister = () => {
    navigate("/register", { state: { from: location.state?.from } });
  };

  return (
    <Container component="main" maxWidth="sm">
      <Box
        sx={{
          marginTop: 8,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          minHeight: "80vh",
        }}
      >
        <Typography variant="h3" component="h1" gutterBottom align="center" sx={{ mb: 4 }}>
          Men's Circle Platform
        </Typography>

        <LoginForm
          onSuccess={handleLoginSuccess}
          onSwitchToRegister={handleSwitchToRegister}
          showTitle={true}
        />
      </Box>
    </Container>
  );
};

export default Login;
