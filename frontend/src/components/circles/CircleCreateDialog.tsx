import React, { useState, useEffect } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  IconButton,
  Typography,
} from "@mui/material";
import { Close as CloseIcon, Add as AddIcon } from "@mui/icons-material";

import CircleForm from "./CircleForm";
import { useCreateCircleMutation, CircleResponse } from "../../store";

interface CircleCreateDialogProps {
  open: boolean;
  onClose: () => void;
  onSuccess: (circle: CircleResponse) => void;
}

const CircleCreateDialog: React.FC<CircleCreateDialogProps> = ({ open, onClose, onSuccess }) => {
  const [createCircle, { isLoading }] = useCreateCircleMutation();
  const [error, setError] = useState<string | null>(null);

  // Reset error when dialog opens
  useEffect(() => {
    if (open) {
      setError(null);
    }
  }, [open]);

  const handleSubmit = async (formData: any) => {
    try {
      setError(null);
      const result = await createCircle(formData).unwrap();
      onSuccess(result);
      onClose();
    } catch (err: any) {
      console.error("Failed to create circle:", err);
      setError(err?.data?.detail || err?.message || "Failed to create circle");
    }
  };

  const handleClose = () => {
    if (!isLoading) {
      onClose();
    }
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      aria-labelledby="create-circle-dialog-title"
      aria-describedby="create-circle-dialog-description"
    >
      <DialogTitle
        id="create-circle-dialog-title"
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          pb: 1,
        }}
      >
        <Typography variant="h6" component="div" sx={{ display: "flex", alignItems: "center" }}>
          <AddIcon sx={{ mr: 1 }} />
          Create New Circle
        </Typography>
        <IconButton
          aria-label="close"
          onClick={handleClose}
          disabled={isLoading}
          sx={{
            color: (theme) => theme.palette.grey[500],
          }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent id="create-circle-dialog-description" dividers>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <CircleForm
          mode="create"
          onSubmit={handleSubmit}
          onCancel={handleClose}
          isLoading={isLoading}
        />
      </DialogContent>
    </Dialog>
  );
};

export default CircleCreateDialog;
