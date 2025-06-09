import React, { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Container, CircularProgress, Typography, Alert, Card, CardContent } from "@mui/material";
import { useDispatch } from "react-redux";
import { useGoogleOAuthCallbackMutation, setCredentials, GoogleOAuthResponse } from "../store";

export const GoogleOAuthCallback: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const [searchParams] = useSearchParams();
  const [googleOAuthCallback] = useGoogleOAuthCallbackMutation();

  const [isProcessing, setIsProcessing] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Get parameters from URL
        const code = searchParams.get("code");
        const state = searchParams.get("state");
        const error = searchParams.get("error");
        const errorDescription = searchParams.get("error_description");

        // Check for OAuth errors
        if (error) {
          const errorMsg = errorDescription || error || "Google OAuth error";
          setError(errorMsg);

          // Post error message to parent window (for popup flow)
          if (window.opener) {
            window.opener.postMessage(
              {
                type: "GOOGLE_OAUTH_ERROR",
                error: errorMsg,
              },
              window.location.origin,
            );
            window.close();
            return;
          }

          setIsProcessing(false);
          return;
        }

        // Check for authorization code
        if (!code) {
          const errorMsg = "No authorization code received from Google";
          setError(errorMsg);

          // Post error message to parent window (for popup flow)
          if (window.opener) {
            window.opener.postMessage(
              {
                type: "GOOGLE_OAUTH_ERROR",
                error: errorMsg,
              },
              window.location.origin,
            );
            window.close();
            return;
          }

          setIsProcessing(false);
          return;
        }

        // Get stored redirect URI from sessionStorage
        const storedRedirectUri = sessionStorage.getItem("google_oauth_redirect_uri");
        const redirectUri = storedRedirectUri || `${window.location.origin}/auth/google/callback`;

        // Exchange code for tokens
        const result = await googleOAuthCallback({
          code,
          state: state || undefined,
          redirect_uri: redirectUri,
        }).unwrap();

        // Handle successful authentication
        handleAuthSuccess(result);
      } catch (err: any) {
        const errorMsg = err?.data?.detail || "Failed to complete Google authentication";
        setError(errorMsg);

        // Post error message to parent window (for popup flow)
        if (window.opener) {
          window.opener.postMessage(
            {
              type: "GOOGLE_OAUTH_ERROR",
              error: errorMsg,
            },
            window.location.origin,
          );
          window.close();
          return;
        }

        setIsProcessing(false);
      }
    };

    handleCallback();
  }, [searchParams, googleOAuthCallback]);

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

    // Clean up session storage
    sessionStorage.removeItem("google_oauth_redirect_uri");
    sessionStorage.removeItem("google_oauth_state");

    // Handle popup flow
    if (window.opener) {
      window.opener.postMessage(
        {
          type: "GOOGLE_OAUTH_SUCCESS",
          result: result,
        },
        window.location.origin,
      );
      window.close();
      return;
    }

    // Handle redirect flow - navigate to dashboard
    setIsProcessing(false);
    navigate("/dashboard", { replace: true });
  };

  const handleRetry = () => {
    navigate("/login", { replace: true });
  };

  if (isProcessing) {
    return (
      <Container maxWidth="sm" sx={{ py: 8 }}>
        <Card>
          <CardContent sx={{ textAlign: "center", py: 6 }}>
            <CircularProgress size={60} sx={{ mb: 3 }} />
            <Typography variant="h6" gutterBottom>
              Completing Google Sign-In
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Please wait while we securely process your authentication...
            </Typography>
          </CardContent>
        </Card>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="sm" sx={{ py: 8 }}>
        <Card>
          <CardContent sx={{ textAlign: "center", py: 4 }}>
            <Alert
              severity="error"
              sx={{ mb: 3 }}
              action={
                <Typography
                  variant="button"
                  sx={{ cursor: "pointer", textDecoration: "underline" }}
                  onClick={handleRetry}
                >
                  Try Again
                </Typography>
              }
            >
              <Typography variant="h6" gutterBottom>
                Authentication Failed
              </Typography>
              <Typography variant="body2">{error}</Typography>
            </Alert>

            <Typography variant="body2" color="text.secondary">
              If you continue to experience issues, please contact support or try a different
              sign-in method.
            </Typography>
          </CardContent>
        </Card>
      </Container>
    );
  }

  // This should not be reached, but just in case
  return (
    <Container maxWidth="sm" sx={{ py: 8 }}>
      <Card>
        <CardContent sx={{ textAlign: "center", py: 4 }}>
          <Typography variant="h6" gutterBottom>
            Authentication Complete
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Redirecting you to the dashboard...
          </Typography>
        </CardContent>
      </Card>
    </Container>
  );
};

export default GoogleOAuthCallback;
