import React from "react";
import { Container, Box, Typography, Paper } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { PhoneVerificationForm } from "../components/auth";
import { useGetCurrentUserQuery } from "../store";

export const PhoneVerification: React.FC = () => {
  const navigate = useNavigate();
  const { data: currentUser } = useGetCurrentUserQuery();

  const handleVerificationSuccess = () => {
    // Navigate to dashboard or wherever appropriate after successful verification
    navigate("/dashboard");
  };

  const handleSkip = () => {
    // Allow user to skip verification and continue to dashboard
    navigate("/dashboard");
  };

  return (
    <Container maxWidth="sm" sx={{ py: 4 }}>
      <Box textAlign="center" mb={4}>
        <Typography variant="h3" component="h1" gutterBottom>
          Verify Your Phone Number
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Secure your account by verifying your phone number. This helps us protect your account and
          enables important security notifications.
        </Typography>
      </Box>

      <Paper elevation={1} sx={{ p: 2 }}>
        <PhoneVerificationForm
          onSuccess={handleVerificationSuccess}
          onSkip={handleSkip}
          initialPhone={currentUser?.phone || ""}
          showTitle={false}
          allowSkip={true}
        />
      </Paper>

      <Box textAlign="center" mt={3}>
        <Typography variant="body2" color="text.secondary">
          Phone verification is optional but recommended for enhanced security. You can complete
          this step later from your account settings.
        </Typography>
      </Box>
    </Container>
  );
};
