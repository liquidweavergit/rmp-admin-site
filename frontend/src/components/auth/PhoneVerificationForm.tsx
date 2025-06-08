import React, { useState, useEffect } from "react";
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  InputAdornment,
  CircularProgress,
  Step,
  Stepper,
  StepLabel,
  Chip,
} from "@mui/material";
import { Phone, Sms, CheckCircle } from "@mui/icons-material";
import {
  useSendSMSVerificationMutation,
  useVerifySMSCodeMutation,
  useGetCurrentUserQuery,
} from "../../store";
import { validatePhone } from "../../utils/validation";

interface PhoneVerificationFormProps {
  onSuccess?: () => void;
  onSkip?: () => void;
  initialPhone?: string;
  showTitle?: boolean;
  allowSkip?: boolean;
}

const steps = ["Enter Phone Number", "Verify Code", "Complete"];

export const PhoneVerificationForm: React.FC<PhoneVerificationFormProps> = ({
  onSuccess,
  onSkip,
  initialPhone = "",
  showTitle = true,
  allowSkip = true,
}) => {
  const [sendSMSVerification, { isLoading: isSending }] = useSendSMSVerificationMutation();
  const [verifySMSCode, { isLoading: isVerifying }] = useVerifySMSCodeMutation();
  const { refetch: refetchUser } = useGetCurrentUserQuery();

  const [activeStep, setActiveStep] = useState(0);
  const [phone, setPhone] = useState(initialPhone);
  const [verificationCode, setVerificationCode] = useState("");
  const [phoneError, setPhoneError] = useState<string>("");
  const [codeError, setCodeError] = useState<string>("");
  const [generalError, setGeneralError] = useState<string>("");
  const [cooldownTime, setCooldownTime] = useState(0);
  const [attemptsRemaining, setAttemptsRemaining] = useState(3);

  // Cooldown timer
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (cooldownTime > 0) {
      interval = setInterval(() => {
        setCooldownTime((prev) => prev - 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [cooldownTime]);

  const handlePhoneChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setPhone(value);
    if (phoneError) {
      setPhoneError("");
    }
    if (generalError) {
      setGeneralError("");
    }
  };

  const handleCodeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value.replace(/\D/g, "").slice(0, 6); // Only digits, max 6
    setVerificationCode(value);
    if (codeError) {
      setCodeError("");
    }
    if (generalError) {
      setGeneralError("");
    }
  };

  const handleSendCode = async () => {
    // Clear previous errors
    setPhoneError("");
    setGeneralError("");

    // Validate phone number
    const phoneValidation = validatePhone(phone);
    if (!phoneValidation.isValid) {
      setPhoneError(phoneValidation.errors.join(", "));
      return;
    }

    try {
      const result = await sendSMSVerification({ phone }).unwrap();

      if (result.success) {
        setActiveStep(1);
        setCooldownTime(60); // 60 second cooldown
        setAttemptsRemaining(3); // Reset attempts for new code
      } else {
        setGeneralError(result.message || "Failed to send verification code");
      }
    } catch (error: any) {
      console.error("SMS send failed:", error);

      if (error.data?.detail) {
        if (typeof error.data.detail === "string") {
          setGeneralError(error.data.detail);
        } else {
          setGeneralError("Failed to send verification code. Please try again.");
        }
      } else if (error.status === 429) {
        setGeneralError("Too many attempts. Please wait before trying again.");
        setCooldownTime(300); // 5 minute cooldown for rate limiting
      } else if (error.status === 422) {
        setPhoneError("Invalid phone number format");
      } else {
        setGeneralError("Failed to send verification code. Please try again.");
      }
    }
  };

  const handleVerifyCode = async () => {
    // Clear previous errors
    setCodeError("");
    setGeneralError("");

    // Validate code
    if (!verificationCode || verificationCode.length !== 6) {
      setCodeError("Please enter a 6-digit verification code");
      return;
    }

    try {
      const result = await verifySMSCode({
        phone,
        code: verificationCode,
      }).unwrap();

      if (result.success && result.phone_verified) {
        setActiveStep(2);
        // Refresh user data to update phone_verified status
        await refetchUser();

        // Complete after a brief delay to show success
        setTimeout(() => {
          if (onSuccess) {
            onSuccess();
          }
        }, 1500);
      } else {
        setCodeError(result.message || "Invalid verification code");
        setAttemptsRemaining((prev) => Math.max(0, prev - 1));

        if (attemptsRemaining <= 1) {
          setGeneralError("Too many failed attempts. Please request a new code.");
          setActiveStep(0);
          setVerificationCode("");
        }
      }
    } catch (error: any) {
      console.error("Code verification failed:", error);

      if (error.data?.detail) {
        if (typeof error.data.detail === "string") {
          setCodeError(error.data.detail);
        } else {
          setCodeError("Invalid verification code");
        }
      } else if (error.status === 400) {
        setCodeError("Invalid or expired verification code");
      } else if (error.status === 429) {
        setGeneralError("Too many attempts. Please wait before trying again.");
      } else {
        setCodeError("Verification failed. Please try again.");
      }

      setAttemptsRemaining((prev) => Math.max(0, prev - 1));

      if (attemptsRemaining <= 1) {
        setGeneralError("Too many failed attempts. Please request a new code.");
        setActiveStep(0);
        setVerificationCode("");
      }
    }
  };

  const handleResendCode = async () => {
    setVerificationCode("");
    setCodeError("");
    await handleSendCode();
  };

  const formatCooldownTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return mins > 0 ? `${mins}:${secs.toString().padStart(2, "0")}` : `${secs}s`;
  };

  return (
    <Card sx={{ maxWidth: 500, width: "100%", mx: "auto" }}>
      <CardContent sx={{ p: 3 }}>
        {showTitle && (
          <Typography variant="h4" component="h1" gutterBottom align="center">
            Verify Phone Number
          </Typography>
        )}

        <Stepper activeStep={activeStep} sx={{ mb: 3 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {generalError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {generalError}
          </Alert>
        )}

        <Box>
          {/* Step 1: Phone Number Entry */}
          {activeStep === 0 && (
            <Box>
              <Typography variant="body1" gutterBottom>
                Enter your phone number to receive a verification code via SMS.
              </Typography>

              <TextField
                fullWidth
                label="Phone Number"
                type="tel"
                value={phone}
                onChange={handlePhoneChange}
                error={!!phoneError}
                helperText={phoneError || "Format: +1 (555) 123-4567 or 5551234567"}
                margin="normal"
                autoComplete="tel"
                autoFocus
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Phone />
                    </InputAdornment>
                  ),
                }}
              />

              <Button
                fullWidth
                variant="contained"
                size="large"
                onClick={handleSendCode}
                disabled={isSending || cooldownTime > 0 || !phone.trim()}
                sx={{ mt: 2, mb: 2 }}
              >
                {isSending ? (
                  <>
                    <CircularProgress size={20} sx={{ mr: 1 }} />
                    Sending Code...
                  </>
                ) : cooldownTime > 0 ? (
                  `Resend in ${formatCooldownTime(cooldownTime)}`
                ) : (
                  "Send Verification Code"
                )}
              </Button>
            </Box>
          )}

          {/* Step 2: Code Verification */}
          {activeStep === 1 && (
            <Box>
              <Typography variant="body1" gutterBottom>
                Enter the 6-digit verification code sent to:
              </Typography>
              <Chip label={phone} color="primary" variant="outlined" sx={{ mb: 2 }} />

              <TextField
                fullWidth
                label="Verification Code"
                value={verificationCode}
                onChange={handleCodeChange}
                error={!!codeError}
                helperText={
                  codeError ||
                  `${attemptsRemaining} attempt${attemptsRemaining !== 1 ? "s" : ""} remaining`
                }
                margin="normal"
                autoComplete="one-time-code"
                autoFocus
                inputProps={{
                  maxLength: 6,
                  pattern: "[0-9]*",
                  inputMode: "numeric",
                }}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Sms />
                    </InputAdornment>
                  ),
                }}
              />

              <Button
                fullWidth
                variant="contained"
                size="large"
                onClick={handleVerifyCode}
                disabled={isVerifying || verificationCode.length !== 6}
                sx={{ mt: 2, mb: 1 }}
              >
                {isVerifying ? (
                  <>
                    <CircularProgress size={20} sx={{ mr: 1 }} />
                    Verifying...
                  </>
                ) : (
                  "Verify Code"
                )}
              </Button>

              <Button
                fullWidth
                variant="text"
                onClick={handleResendCode}
                disabled={cooldownTime > 0 || isSending}
                sx={{ mb: 2 }}
              >
                {cooldownTime > 0
                  ? `Resend code in ${formatCooldownTime(cooldownTime)}`
                  : "Resend Code"}
              </Button>

              <Button fullWidth variant="text" onClick={() => setActiveStep(0)}>
                Change Phone Number
              </Button>
            </Box>
          )}

          {/* Step 3: Success */}
          {activeStep === 2 && (
            <Box textAlign="center">
              <CheckCircle color="success" sx={{ fontSize: 64, mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Phone Number Verified!
              </Typography>
              <Typography variant="body1" color="text.secondary" gutterBottom>
                Your phone number has been successfully verified.
              </Typography>
            </Box>
          )}

          {/* Skip Option */}
          {allowSkip && activeStep < 2 && onSkip && (
            <Box textAlign="center" sx={{ mt: 2 }}>
              <Button variant="text" onClick={onSkip} color="secondary">
                Skip for now
              </Button>
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};
