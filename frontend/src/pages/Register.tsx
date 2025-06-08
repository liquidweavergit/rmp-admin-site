import React, { useState } from "react";
import { Container, Box, Typography, Alert } from "@mui/material";
import { useNavigate, useLocation } from "react-router-dom";
import { RegisterForm } from "../components/auth";

export const Register: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [showSuccess, setShowSuccess] = useState(false);

  const handleRegistrationSuccess = () => {
    setShowSuccess(true);
    // After a short delay, redirect to login
    setTimeout(() => {
      navigate("/login", {
        state: {
          from: location.state?.from,
          message: "Registration successful! Please sign in with your new account.",
        },
      });
    }, 2000);
  };

  const handleSwitchToLogin = () => {
    navigate("/login", { state: { from: location.state?.from } });
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

        {showSuccess && (
          <Alert severity="success" sx={{ mb: 3, width: "100%", maxWidth: 500 }}>
            Account created successfully! Redirecting to sign in...
          </Alert>
        )}

        <RegisterForm
          onSuccess={handleRegistrationSuccess}
          onSwitchToLogin={handleSwitchToLogin}
          showTitle={true}
        />
      </Box>
    </Container>
  );
};

export default Register;
