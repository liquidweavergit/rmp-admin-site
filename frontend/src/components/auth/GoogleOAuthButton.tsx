import React, { useState, useEffect, useCallback } from "react";
import { Button, Box, Alert, CircularProgress, Divider, Typography } from "@mui/material";
import { Google } from "@mui/icons-material";
import {
  useGetGoogleAuthUrlMutation,
  useGoogleOAuthLoginMutation,
  setCredentials,
  GoogleOAuthResponse,
} from "../../store";
import { useDispatch } from "react-redux";

// Declare global google object for TypeScript
declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: any) => void;
          renderButton: (element: HTMLElement, config: any) => void;
          prompt: () => void;
        };
      };
    };
    handleGoogleCredentialResponse?: (response: any) => void;
  }
}

interface GoogleOAuthButtonProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
  mode?: "redirect" | "popup" | "oneTap";
  size?: "small" | "medium" | "large";
  variant?: "contained" | "outlined" | "text";
  fullWidth?: boolean;
  disabled?: boolean;
  showDivider?: boolean;
  dividerText?: string;
}

export const GoogleOAuthButton: React.FC<GoogleOAuthButtonProps> = ({
  onSuccess,
  onError,
  mode = "oneTap",
  size = "medium",
  variant = "outlined",
  fullWidth = false,
  disabled = false,
  showDivider = false,
  dividerText = "or",
}) => {
  const dispatch = useDispatch();

  const [getGoogleAuthUrl] = useGetGoogleAuthUrlMutation();
  const [googleOAuthLogin] = useGoogleOAuthLoginMutation();

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isGoogleLoaded, setIsGoogleLoaded] = useState(false);

  // Load Google One Tap script
  useEffect(() => {
    if (mode !== "oneTap") return;

    const script = document.createElement("script");
    script.src = "https://accounts.google.com/gsi/client";
    script.async = true;
    script.defer = true;
    script.onload = () => setIsGoogleLoaded(true);
    document.head.appendChild(script);

    return () => {
      const existingScript = document.querySelector(
        'script[src="https://accounts.google.com/gsi/client"]',
      );
      if (existingScript) {
        existingScript.remove();
      }
    };
  }, [mode]);

  // Initialize Google One Tap
  useEffect(() => {
    if (!isGoogleLoaded || !window.google || mode !== "oneTap") return;

    // Define callback function globally
    window.handleGoogleCredentialResponse = handleGoogleCredentialResponse;

    window.google.accounts.id.initialize({
      client_id: process.env.REACT_APP_GOOGLE_CLIENT_ID,
      callback: "handleGoogleCredentialResponse",
      auto_select: false,
      cancel_on_tap_outside: true,
    });

    // Show One Tap prompt
    if (!disabled) {
      window.google.accounts.id.prompt();
    }
  }, [isGoogleLoaded, disabled, mode]);

  const handleGoogleCredentialResponse = useCallback(
    async (response: any) => {
      if (!response.credential) {
        const errorMsg = "No credential received from Google";
        setError(errorMsg);
        onError?.(errorMsg);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const result = await googleOAuthLogin({
          id_token: response.credential,
        }).unwrap();

        handleAuthSuccess(result);
      } catch (err: any) {
        const errorMsg = err?.data?.detail || "Google authentication failed";
        setError(errorMsg);
        onError?.(errorMsg);
      } finally {
        setIsLoading(false);
      }
    },
    [googleOAuthLogin, onError, onSuccess],
  );

  const handleAuthSuccess = (result: GoogleOAuthResponse) => {
    // Store credentials in Redux
    dispatch(
      setCredentials({
        tokens: {
          access_token: result.access_token,
          refresh_token: result.refresh_token,
          token_type: result.token_type,
        },
        user: result.user,
      }),
    );

    onSuccess?.();
  };

  const handleRedirectFlow = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const currentUrl = window.location.origin;
      const redirectUri = `${currentUrl}/auth/google/callback`;

      const result = await getGoogleAuthUrl({
        redirect_uri: redirectUri,
      }).unwrap();

      // Store redirect URI and state in sessionStorage for callback
      sessionStorage.setItem("google_oauth_redirect_uri", redirectUri);
      if (result.state) {
        sessionStorage.setItem("google_oauth_state", result.state);
      }

      // Redirect to Google OAuth
      window.location.href = result.authorization_url;
    } catch (err: any) {
      const errorMsg = err?.data?.detail || "Failed to get Google authorization URL";
      setError(errorMsg);
      onError?.(errorMsg);
      setIsLoading(false);
    }
  };

  const handlePopupFlow = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const currentUrl = window.location.origin;
      const redirectUri = `${currentUrl}/auth/google/callback`;

      const result = await getGoogleAuthUrl({
        redirect_uri: redirectUri,
      }).unwrap();

      // Open popup window
      const popup = window.open(
        result.authorization_url,
        "google-oauth",
        "width=500,height=600,scrollbars=yes,resizable=yes",
      );

      if (!popup) {
        throw new Error("Popup blocked. Please allow popups for this site.");
      }

      // Listen for popup completion
      const checkClosed = setInterval(() => {
        if (popup.closed) {
          clearInterval(checkClosed);
          setIsLoading(false);

          // Check if auth was successful by looking for stored tokens
          const storedToken = localStorage.getItem("access_token");
          if (storedToken) {
            onSuccess?.();
          } else {
            setError("Authentication cancelled or failed");
            onError?.("Authentication cancelled or failed");
          }
        }
      }, 1000);

      // Handle popup message
      const handleMessage = (event: MessageEvent) => {
        if (event.origin !== window.location.origin) return;

        if (event.data.type === "GOOGLE_OAUTH_SUCCESS") {
          clearInterval(checkClosed);
          popup.close();
          handleAuthSuccess(event.data.result);
          setIsLoading(false);
        } else if (event.data.type === "GOOGLE_OAUTH_ERROR") {
          clearInterval(checkClosed);
          popup.close();
          setError(event.data.error);
          onError?.(event.data.error);
          setIsLoading(false);
        }
      };

      window.addEventListener("message", handleMessage);

      // Cleanup
      setTimeout(
        () => {
          if (!popup.closed) {
            popup.close();
            clearInterval(checkClosed);
            setIsLoading(false);
            setError("Authentication timeout");
            onError?.("Authentication timeout");
          }
          window.removeEventListener("message", handleMessage);
        },
        5 * 60 * 1000,
      ); // 5 minute timeout
    } catch (err: any) {
      const errorMsg = err?.data?.detail || err.message || "Failed to start Google authentication";
      setError(errorMsg);
      onError?.(errorMsg);
      setIsLoading(false);
    }
  };

  const handleButtonClick = () => {
    if (disabled || isLoading) return;

    switch (mode) {
      case "redirect":
        handleRedirectFlow();
        break;
      case "popup":
        handlePopupFlow();
        break;
      case "oneTap":
        // One Tap is auto-initialized, but we can trigger it manually
        if (window.google) {
          window.google.accounts.id.prompt();
        }
        break;
    }
  };

  const getButtonSize = () => {
    switch (size) {
      case "small":
        return { height: 36, fontSize: "0.875rem" };
      case "large":
        return { height: 56, fontSize: "1rem" };
      default:
        return { height: 42, fontSize: "0.875rem" };
    }
  };

  const buttonStyle = getButtonSize();

  return (
    <Box sx={{ width: fullWidth ? "100%" : "auto" }}>
      {showDivider && (
        <Box sx={{ my: 2 }}>
          <Divider>
            <Typography variant="body2" color="text.secondary">
              {dividerText}
            </Typography>
          </Divider>
        </Box>
      )}

      <Button
        variant={variant}
        fullWidth={fullWidth}
        onClick={handleButtonClick}
        disabled={disabled || isLoading}
        startIcon={isLoading ? <CircularProgress size={20} /> : <Google />}
        sx={{
          height: buttonStyle.height,
          fontSize: buttonStyle.fontSize,
          textTransform: "none",
          borderColor: variant === "outlined" ? "#dadce0" : undefined,
          color: variant === "outlined" ? "#3c4043" : undefined,
          "&:hover": {
            borderColor: variant === "outlined" ? "#dadce0" : undefined,
            backgroundColor: variant === "outlined" ? "#f8f9fa" : undefined,
          },
        }}
      >
        {isLoading
          ? "Signing in..."
          : mode === "oneTap"
            ? "Sign in with Google"
            : "Continue with Google"}
      </Button>

      {error && (
        <Alert severity="error" sx={{ mt: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
    </Box>
  );
};

export default GoogleOAuthButton;
