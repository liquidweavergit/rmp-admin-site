import React, { useState } from "react";
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  IconButton,
  InputAdornment,
  Link,
  CircularProgress,
  Grid,
} from "@mui/material";
import { Visibility, VisibilityOff, Email, Lock, Person, Phone } from "@mui/icons-material";
import { useDispatch } from "react-redux";
import { useRegisterMutation } from "../../store";
import { setCredentials } from "../../store";
import { validateRegisterForm, RegisterFormData } from "../../utils/validation";

interface RegisterFormProps {
  onSuccess?: () => void;
  onSwitchToLogin?: () => void;
  showTitle?: boolean;
}

export const RegisterForm: React.FC<RegisterFormProps> = ({
  onSuccess,
  onSwitchToLogin,
  showTitle = true,
}) => {
  const dispatch = useDispatch();
  const [register, { isLoading }] = useRegisterMutation();

  const [formData, setFormData] = useState<RegisterFormData>({
    email: "",
    password: "",
    confirmPassword: "",
    first_name: "",
    last_name: "",
    phone: "",
  });

  const [fieldErrors, setFieldErrors] = useState<Record<string, string[]>>({});
  const [generalError, setGeneralError] = useState<string>("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const handleInputChange =
    (field: keyof RegisterFormData) => (event: React.ChangeEvent<HTMLInputElement>) => {
      const value = event.target.value;
      setFormData((prev) => ({ ...prev, [field]: value }));

      // Clear field error when user starts typing
      if (fieldErrors[field]) {
        setFieldErrors((prev) => {
          const newErrors = { ...prev };
          delete newErrors[field];
          return newErrors;
        });
      }

      // Clear general error when user starts typing
      if (generalError) {
        setGeneralError("");
      }
    };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    // Clear previous errors
    setFieldErrors({});
    setGeneralError("");

    // Validate form
    const validation = validateRegisterForm(formData);
    if (!validation.isValid) {
      setFieldErrors(validation.fieldErrors);
      return;
    }

    try {
      // Prepare data for API (exclude confirmPassword and empty phone)
      const registerData = {
        email: formData.email,
        password: formData.password,
        first_name: formData.first_name.trim(),
        last_name: formData.last_name.trim(),
        ...(formData.phone?.trim() && { phone: formData.phone.trim() }),
      };

      const user = await register(registerData).unwrap();

      // For registration, we don't get tokens directly
      // User needs to verify email or we need to automatically log them in
      // For now, we'll show success and let them log in
      if (onSuccess) {
        onSuccess();
      }
    } catch (error: any) {
      console.error("Registration failed:", error);

      if (error.data?.detail) {
        if (typeof error.data.detail === "string") {
          setGeneralError(error.data.detail);
        } else if (Array.isArray(error.data.detail)) {
          // Handle validation errors from backend
          const backendErrors: Record<string, string[]> = {};
          error.data.detail.forEach((err: any) => {
            if (err.loc && err.loc.length > 1) {
              const field = err.loc[err.loc.length - 1];
              if (!backendErrors[field]) {
                backendErrors[field] = [];
              }
              backendErrors[field].push(err.msg);
            }
          });

          if (Object.keys(backendErrors).length > 0) {
            setFieldErrors(backendErrors);
          } else {
            setGeneralError("Registration failed. Please check your input.");
          }
        }
      } else if (error.status === 409) {
        setFieldErrors({ email: ["An account with this email already exists"] });
      } else if (error.status === 422) {
        setGeneralError("Please check your input and try again");
      } else {
        setGeneralError("Registration failed. Please try again.");
      }
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const toggleConfirmPasswordVisibility = () => {
    setShowConfirmPassword(!showConfirmPassword);
  };

  return (
    <Card sx={{ maxWidth: 500, width: "100%", mx: "auto" }}>
      <CardContent sx={{ p: 3 }}>
        {showTitle && (
          <Typography variant="h4" component="h1" gutterBottom align="center">
            Create Account
          </Typography>
        )}

        {generalError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {generalError}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit} noValidate>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="First Name"
                value={formData.first_name}
                onChange={handleInputChange("first_name")}
                error={!!fieldErrors.first_name}
                helperText={fieldErrors.first_name?.join(", ")}
                margin="normal"
                required
                autoComplete="given-name"
                autoFocus
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Person />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Last Name"
                value={formData.last_name}
                onChange={handleInputChange("last_name")}
                error={!!fieldErrors.last_name}
                helperText={fieldErrors.last_name?.join(", ")}
                margin="normal"
                required
                autoComplete="family-name"
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Person />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
          </Grid>

          <TextField
            fullWidth
            label="Email"
            type="email"
            value={formData.email}
            onChange={handleInputChange("email")}
            error={!!fieldErrors.email}
            helperText={fieldErrors.email?.join(", ")}
            margin="normal"
            required
            autoComplete="email"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Email />
                </InputAdornment>
              ),
            }}
          />

          <TextField
            fullWidth
            label="Phone (Optional)"
            type="tel"
            value={formData.phone}
            onChange={handleInputChange("phone")}
            error={!!fieldErrors.phone}
            helperText={fieldErrors.phone?.join(", ") || "Format: +1 (555) 123-4567 or 5551234567"}
            margin="normal"
            autoComplete="tel"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Phone />
                </InputAdornment>
              ),
            }}
          />

          <TextField
            fullWidth
            label="Password"
            type={showPassword ? "text" : "password"}
            value={formData.password}
            onChange={handleInputChange("password")}
            error={!!fieldErrors.password}
            helperText={
              fieldErrors.password?.join(", ") ||
              "Must be 8+ characters with uppercase, lowercase, and digit"
            }
            margin="normal"
            required
            autoComplete="new-password"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Lock />
                </InputAdornment>
              ),
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    aria-label="toggle password visibility"
                    onClick={togglePasswordVisibility}
                    edge="end"
                  >
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />

          <TextField
            fullWidth
            label="Confirm Password"
            type={showConfirmPassword ? "text" : "password"}
            value={formData.confirmPassword}
            onChange={handleInputChange("confirmPassword")}
            error={!!fieldErrors.confirmPassword}
            helperText={fieldErrors.confirmPassword?.join(", ")}
            margin="normal"
            required
            autoComplete="new-password"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Lock />
                </InputAdornment>
              ),
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    aria-label="toggle confirm password visibility"
                    onClick={toggleConfirmPasswordVisibility}
                    edge="end"
                  >
                    {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />

          <Button
            type="submit"
            fullWidth
            variant="contained"
            size="large"
            disabled={isLoading}
            sx={{ mt: 3, mb: 2 }}
          >
            {isLoading ? (
              <>
                <CircularProgress size={20} sx={{ mr: 1 }} />
                Creating Account...
              </>
            ) : (
              "Create Account"
            )}
          </Button>

          {onSwitchToLogin && (
            <Box textAlign="center">
              <Typography variant="body2">
                Already have an account?{" "}
                <Link
                  component="button"
                  variant="body2"
                  type="button"
                  onClick={(e) => {
                    e.preventDefault();
                    onSwitchToLogin();
                  }}
                  sx={{ textDecoration: "underline", cursor: "pointer" }}
                >
                  Sign in here
                </Link>
              </Typography>
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};
