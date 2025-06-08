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
} from "@mui/material";
import { Visibility, VisibilityOff, Email, Lock } from "@mui/icons-material";
import { useDispatch } from "react-redux";
import { useLoginMutation } from "../../store";
import { setCredentials } from "../../store";
import { validateLoginForm, LoginFormData } from "../../utils/validation";

interface LoginFormProps {
  onSuccess?: () => void;
  onSwitchToRegister?: () => void;
  showTitle?: boolean;
}

export const LoginForm: React.FC<LoginFormProps> = ({
  onSuccess,
  onSwitchToRegister,
  showTitle = true,
}) => {
  const dispatch = useDispatch();
  const [login, { isLoading }] = useLoginMutation();

  const [formData, setFormData] = useState<LoginFormData>({
    email: "",
    password: "",
  });

  const [fieldErrors, setFieldErrors] = useState<Record<string, string[]>>({});
  const [generalError, setGeneralError] = useState<string>("");
  const [showPassword, setShowPassword] = useState(false);

  const handleInputChange =
    (field: keyof LoginFormData) => (event: React.ChangeEvent<HTMLInputElement>) => {
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
    const validation = validateLoginForm(formData);
    if (!validation.isValid) {
      setFieldErrors(validation.fieldErrors);
      return;
    }

    try {
      const result = await login(formData).unwrap();

      // Store tokens and mark as authenticated
      dispatch(setCredentials({ tokens: result }));

      if (onSuccess) {
        onSuccess();
      }
    } catch (error: any) {
      console.error("Login failed:", error);

      if (error.data?.detail) {
        setGeneralError(error.data.detail);
      } else if (error.status === 401) {
        setGeneralError("Invalid email or password");
      } else if (error.status === 422) {
        // Validation errors from backend
        if (error.data?.detail && Array.isArray(error.data.detail)) {
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
          setFieldErrors(backendErrors);
        } else {
          setGeneralError("Please check your input and try again");
        }
      } else {
        setGeneralError("Login failed. Please try again.");
      }
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <Card sx={{ maxWidth: 400, width: "100%", mx: "auto" }}>
      <CardContent sx={{ p: 3 }}>
        {showTitle && (
          <Typography variant="h4" component="h1" gutterBottom align="center">
            Sign In
          </Typography>
        )}

        {generalError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {generalError}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit} noValidate>
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
            autoFocus
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
            label="Password"
            type={showPassword ? "text" : "password"}
            value={formData.password}
            onChange={handleInputChange("password")}
            error={!!fieldErrors.password}
            helperText={fieldErrors.password?.join(", ")}
            margin="normal"
            required
            autoComplete="current-password"
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
                Signing In...
              </>
            ) : (
              "Sign In"
            )}
          </Button>

          {onSwitchToRegister && (
            <Box textAlign="center">
              <Typography variant="body2">
                Don't have an account?{" "}
                <Link
                  component="button"
                  variant="body2"
                  type="button"
                  onClick={(e) => {
                    e.preventDefault();
                    onSwitchToRegister();
                  }}
                  sx={{ textDecoration: "underline", cursor: "pointer" }}
                >
                  Sign up here
                </Link>
              </Typography>
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};
