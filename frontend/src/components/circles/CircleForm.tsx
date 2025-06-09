import React, { useState, useEffect } from "react";
import {
  Box,
  TextField,
  Button,
  Grid,
  Typography,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Divider,
  SelectChangeEvent,
} from "@mui/material";
import {
  Group as GroupIcon,
  LocationOn as LocationIcon,
  Schedule as ScheduleIcon,
} from "@mui/icons-material";

interface CircleFormData {
  name: string;
  description: string;
  capacity_min: number;
  capacity_max: number;
  location_name: string;
  location_address: string;
  meeting_schedule: {
    day: string;
    time: string;
  } | null;
}

interface CircleData {
  id?: number;
  name: string;
  description?: string;
  capacity_min: number;
  capacity_max: number;
  location_name?: string;
  location_address?: string;
  meeting_schedule?: Record<string, any>;
}

interface CircleFormProps {
  mode: "create" | "edit";
  initialData?: CircleData;
  onSubmit: (data: Partial<CircleFormData>) => void;
  onCancel: () => void;
  isLoading: boolean;
}

const daysOfWeek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

const CircleForm: React.FC<CircleFormProps> = ({
  mode,
  initialData,
  onSubmit,
  onCancel,
  isLoading,
}) => {
  const [formData, setFormData] = useState<CircleFormData>({
    name: "",
    description: "",
    capacity_min: 2,
    capacity_max: 8,
    location_name: "",
    location_address: "",
    meeting_schedule: null,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (mode === "edit" && initialData) {
      setFormData({
        name: initialData.name || "",
        description: initialData.description || "",
        capacity_min: initialData.capacity_min || 2,
        capacity_max: initialData.capacity_max || 8,
        location_name: initialData.location_name || "",
        location_address: initialData.location_address || "",
        meeting_schedule: initialData.meeting_schedule
          ? {
              day: initialData.meeting_schedule.day || "",
              time: initialData.meeting_schedule.time || "",
            }
          : null,
      });
    }
  }, [mode, initialData]);

  const handleInputChange =
    (field: keyof CircleFormData) => (event: React.ChangeEvent<HTMLInputElement>) => {
      const value = event.target.value;
      setFormData((prev) => ({ ...prev, [field]: value }));

      // Clear error when user starts typing
      if (errors[field]) {
        setErrors((prev) => ({ ...prev, [field]: "" }));
      }
    };

  const handleNumberChange =
    (field: "capacity_min" | "capacity_max") => (event: React.ChangeEvent<HTMLInputElement>) => {
      const value = parseInt(event.target.value, 10);
      setFormData((prev) => ({ ...prev, [field]: value }));

      // Clear error when user starts typing
      if (errors[field]) {
        setErrors((prev) => ({ ...prev, [field]: "" }));
      }
    };

  const handleScheduleChange =
    (field: "day" | "time") => (event: React.ChangeEvent<HTMLInputElement>) => {
      const value = event.target.value;
      setFormData((prev) => ({
        ...prev,
        meeting_schedule: prev.meeting_schedule
          ? {
              ...prev.meeting_schedule,
              [field]: value,
            }
          : {
              day: field === "day" ? value : "",
              time: field === "time" ? value : "",
            },
      }));
    };

  const handleDayChange = (event: SelectChangeEvent<string>) => {
    const value = event.target.value;
    setFormData((prev) => ({
      ...prev,
      meeting_schedule: prev.meeting_schedule
        ? {
            ...prev.meeting_schedule,
            day: value,
          }
        : {
            day: value,
            time: "",
          },
    }));
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = "Circle name is required";
    }

    if (formData.capacity_max < formData.capacity_min) {
      newErrors.capacity_max = "Maximum capacity must be greater than or equal to minimum capacity";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();

    if (!validateForm()) {
      return;
    }

    const submitData: Partial<CircleFormData> = {
      name: formData.name.trim(),
      description: formData.description.trim(),
      capacity_min: formData.capacity_min,
      capacity_max: formData.capacity_max,
      location_name: formData.location_name.trim(),
      location_address: formData.location_address.trim(),
      meeting_schedule:
        formData.meeting_schedule?.day && formData.meeting_schedule?.time
          ? formData.meeting_schedule
          : null,
    };

    onSubmit(submitData);
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ width: "100%" }}>
      {isLoading && (
        <Box display="flex" justifyContent="center" mb={2}>
          <CircularProgress size={24} />
        </Box>
      )}

      <Grid container spacing={3}>
        {/* Basic Information */}
        <Grid item xs={12}>
          <Typography variant="h6" gutterBottom sx={{ display: "flex", alignItems: "center" }}>
            <GroupIcon sx={{ mr: 1 }} />
            Circle Information
          </Typography>
        </Grid>

        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Circle Name"
            value={formData.name}
            onChange={handleInputChange("name")}
            error={!!errors.name}
            helperText={errors.name}
            disabled={isLoading}
            required
            inputProps={{ maxLength: 100 }}
          />
        </Grid>

        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Description"
            multiline
            rows={3}
            value={formData.description}
            onChange={handleInputChange("description")}
            disabled={isLoading}
            inputProps={{ maxLength: 1000 }}
            placeholder="Describe the purpose and goals of this circle..."
          />
        </Grid>

        {/* Capacity Settings */}
        <Grid item xs={6}>
          <TextField
            fullWidth
            label="Minimum Capacity"
            type="number"
            value={formData.capacity_min}
            onChange={handleNumberChange("capacity_min")}
            disabled={isLoading}
            InputProps={{
              inputProps: { min: 2, max: 10 },
            }}
          />
        </Grid>

        <Grid item xs={6}>
          <TextField
            fullWidth
            label="Maximum Capacity"
            type="number"
            value={formData.capacity_max}
            onChange={handleNumberChange("capacity_max")}
            error={!!errors.capacity_max}
            helperText={errors.capacity_max}
            disabled={isLoading}
            InputProps={{
              inputProps: { min: 2, max: 10 },
            }}
          />
        </Grid>

        {/* Location Information */}
        <Grid item xs={12}>
          <Divider sx={{ my: 1 }} />
          <Typography variant="h6" gutterBottom sx={{ display: "flex", alignItems: "center" }}>
            <LocationIcon sx={{ mr: 1 }} />
            Location
          </Typography>
        </Grid>

        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Location Name"
            value={formData.location_name}
            onChange={handleInputChange("location_name")}
            disabled={isLoading}
            inputProps={{ maxLength: 200 }}
            placeholder="e.g., Community Center, Office Building"
          />
        </Grid>

        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Location Address"
            value={formData.location_address}
            onChange={handleInputChange("location_address")}
            disabled={isLoading}
            inputProps={{ maxLength: 500 }}
            placeholder="Full address including city, state, and ZIP code"
          />
        </Grid>

        {/* Meeting Schedule */}
        <Grid item xs={12}>
          <Divider sx={{ my: 1 }} />
          <Typography variant="h6" gutterBottom sx={{ display: "flex", alignItems: "center" }}>
            <ScheduleIcon sx={{ mr: 1 }} />
            Meeting Schedule
          </Typography>
        </Grid>

        <Grid item xs={6}>
          <FormControl fullWidth disabled={isLoading}>
            <InputLabel id="day-of-week-label">Day of Week</InputLabel>
            <Select
              labelId="day-of-week-label"
              value={formData.meeting_schedule?.day || ""}
              onChange={handleDayChange}
              label="Day of Week"
            >
              <MenuItem value="">
                <em>Select a day</em>
              </MenuItem>
              {daysOfWeek.map((day) => (
                <MenuItem key={day} value={day}>
                  {day}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={6}>
          <TextField
            fullWidth
            label="Meeting Time"
            type="time"
            value={formData.meeting_schedule?.time || ""}
            onChange={handleScheduleChange("time")}
            disabled={isLoading}
            InputLabelProps={{
              shrink: true,
            }}
          />
        </Grid>

        {/* Action Buttons */}
        <Grid item xs={12}>
          <Box display="flex" gap={2} justifyContent="flex-end" mt={2}>
            <Button variant="outlined" onClick={onCancel} disabled={isLoading}>
              Cancel
            </Button>
            <Button type="submit" variant="contained" disabled={isLoading}>
              {mode === "create" ? "Create Circle" : "Update Circle"}
            </Button>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

export default CircleForm;
