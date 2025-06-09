import React, { useState, useEffect } from "react";
import { Dialog, DialogTitle, DialogContent, Alert, IconButton, Typography } from "@mui/material";
import { Close as CloseIcon, Edit as EditIcon } from "@mui/icons-material";

import CircleForm from "./CircleForm";
import { useUpdateCircleMutation, CircleResponse } from "../../store";

interface CircleEditDialogProps {
  open: boolean;
  circle: CircleResponse | null;
  onClose: () => void;
  onSuccess: (circle: CircleResponse) => void;
}

const CircleEditDialog: React.FC<CircleEditDialogProps> = ({
  open,
  circle,
  onClose,
  onSuccess,
}) => {
  const [updateCircle, { isLoading }] = useUpdateCircleMutation();
  const [error, setError] = useState<string | null>(null);

  // Reset error when dialog opens
  useEffect(() => {
    if (open) {
      setError(null);
    }
  }, [open]);

  const handleSubmit = async (formData: any) => {
    if (!circle) return;

    try {
      setError(null);
      const result = await updateCircle({
        id: circle.id,
        data: formData,
      }).unwrap();
      onSuccess(result);
      onClose();
    } catch (err: any) {
      console.error("Failed to update circle:", err);
      setError(err?.data?.detail || err?.message || "Failed to update circle");
    }
  };

  const handleClose = () => {
    if (!isLoading) {
      onClose();
    }
  };

  // Don't render if dialog is closed or no circle data
  if (!open || !circle) {
    return null;
  }

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      aria-labelledby="edit-circle-dialog-title"
      aria-describedby="edit-circle-dialog-description"
    >
      <DialogTitle
        id="edit-circle-dialog-title"
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          pb: 1,
        }}
      >
        <Typography variant="h6" component="div" sx={{ display: "flex", alignItems: "center" }}>
          <EditIcon sx={{ mr: 1 }} />
          Edit Circle
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

      <DialogContent id="edit-circle-dialog-description" dividers>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <CircleForm
          mode="edit"
          initialData={circle}
          onSubmit={handleSubmit}
          onCancel={handleClose}
          isLoading={isLoading}
        />
      </DialogContent>
    </Dialog>
  );
};

export default CircleEditDialog;
