import React, { useState } from "react";
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  IconButton,
  Menu,
  MenuItem,
  Alert,
  Skeleton,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  ListItemSecondaryAction,
  Divider,
  Paper,
  Stack,
  Tooltip,
  TextField,
  Select,
  FormControl,
  InputLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormHelperText,
} from "@mui/material";
import {
  People as PeopleIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  SwapHoriz as TransferIcon,
  Payment as PaymentIcon,
  MoreVert as MoreVertIcon,
} from "@mui/icons-material";
import { format, parseISO } from "date-fns";

import {
  useGetCircleMembersQuery,
  useGetCirclesQuery,
  useAddCircleMemberMutation,
  useRemoveCircleMemberMutation,
  useTransferCircleMemberMutation,
  useUpdateMemberPaymentStatusMutation,
  CircleResponse,
  CircleMemberListResponse,
  CircleMemberAdd,
  CircleMemberTransfer,
  CircleMemberPaymentUpdate,
} from "../../store";

interface MemberManagementInterfaceProps {
  circle: CircleResponse;
}

interface AddMemberForm {
  user_id: string;
  payment_status: string;
}

interface TransferMemberForm {
  target_circle_id: string;
  reason: string;
}

const MemberManagementInterface: React.FC<MemberManagementInterfaceProps> = ({ circle }) => {
  // State for forms and dialogs
  const [addMemberForm, setAddMemberForm] = useState<AddMemberForm>({
    user_id: "",
    payment_status: "pending",
  });
  const [addMemberErrors, setAddMemberErrors] = useState<Record<string, string>>({});
  const [removeDialogOpen, setRemoveDialogOpen] = useState(false);
  const [memberToRemove, setMemberToRemove] = useState<number | null>(null);
  const [transferDialogOpen, setTransferDialogOpen] = useState(false);
  const [memberToTransfer, setMemberToTransfer] = useState<number | null>(null);
  const [transferForm, setTransferForm] = useState<TransferMemberForm>({
    target_circle_id: "",
    reason: "",
  });
  const [transferErrors, setTransferErrors] = useState<Record<string, string>>({});
  const [paymentMenuAnchor, setPaymentMenuAnchor] = useState<null | HTMLElement>(null);
  const [paymentMenuMember, setPaymentMenuMember] = useState<number | null>(null);
  const [errorMessage, setErrorMessage] = useState<string>("");

  // API hooks
  const {
    data: members,
    isLoading: membersLoading,
    error: membersError,
    refetch: refetchMembers,
  } = useGetCircleMembersQuery(circle.id);

  const { data: circles = [] } = useGetCirclesQuery();

  const [addMember, { isLoading: addingMember }] = useAddCircleMemberMutation();
  const [removeMember, { isLoading: removingMember }] = useRemoveCircleMemberMutation();
  const [transferMember, { isLoading: transferringMember }] = useTransferCircleMemberMutation();
  const [updatePaymentStatus, { isLoading: updatingPayment }] =
    useUpdateMemberPaymentStatusMutation();

  // Helper functions
  const getPaymentStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "current":
        return "success";
      case "pending":
        return "warning";
      case "overdue":
        return "error";
      case "paused":
        return "default";
      default:
        return "default";
    }
  };

  const validateAddMemberForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!addMemberForm.user_id.trim()) {
      errors.user_id = "User ID is required";
    } else if (isNaN(Number(addMemberForm.user_id))) {
      errors.user_id = "User ID must be a number";
    }

    setAddMemberErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const validateTransferForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!transferForm.target_circle_id) {
      errors.target_circle_id = "Target circle is required";
    }

    setTransferErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Event handlers
  const handleAddMember = async () => {
    if (!validateAddMemberForm()) return;

    try {
      setErrorMessage("");
      const memberData: CircleMemberAdd = {
        user_id: Number(addMemberForm.user_id),
        payment_status: addMemberForm.payment_status,
      };

      await addMember({
        circleId: circle.id,
        member: memberData,
      }).unwrap();

      // Reset form
      setAddMemberForm({ user_id: "", payment_status: "pending" });
      refetchMembers();
    } catch (error: any) {
      const errorMsg = error?.data?.detail || "Failed to add member";
      setErrorMessage(errorMsg);
    }
  };

  const handleRemoveMember = (userId: number) => {
    setMemberToRemove(userId);
    setRemoveDialogOpen(true);
  };

  const confirmRemoveMember = async () => {
    if (!memberToRemove) return;

    try {
      setErrorMessage("");
      await removeMember({
        circleId: circle.id,
        userId: memberToRemove,
      }).unwrap();

      setRemoveDialogOpen(false);
      setMemberToRemove(null);
      refetchMembers();
    } catch (error: any) {
      const errorMsg = error?.data?.detail || "Failed to remove member";
      setErrorMessage(errorMsg);
    }
  };

  const handleTransferMember = (userId: number) => {
    setMemberToTransfer(userId);
    setTransferDialogOpen(true);
    setTransferForm({ target_circle_id: "", reason: "" });
    setTransferErrors({});
  };

  const confirmTransferMember = async () => {
    if (!memberToTransfer || !validateTransferForm()) return;

    try {
      setErrorMessage("");
      const transferData: CircleMemberTransfer = {
        target_circle_id: Number(transferForm.target_circle_id),
        reason: transferForm.reason || undefined,
      };

      await transferMember({
        circleId: circle.id,
        userId: memberToTransfer,
        transfer_data: transferData,
      }).unwrap();

      setTransferDialogOpen(false);
      setMemberToTransfer(null);
      refetchMembers();
    } catch (error: any) {
      const errorMsg = error?.data?.detail || "Failed to transfer member";
      setErrorMessage(errorMsg);
    }
  };

  const handlePaymentStatusClick = (event: React.MouseEvent<HTMLElement>, userId: number) => {
    setPaymentMenuAnchor(event.currentTarget);
    setPaymentMenuMember(userId);
  };

  const handlePaymentStatusUpdate = async (newStatus: string) => {
    if (!paymentMenuMember) return;

    try {
      setErrorMessage("");
      const paymentData: CircleMemberPaymentUpdate = {
        payment_status: newStatus,
      };

      await updatePaymentStatus({
        circleId: circle.id,
        userId: paymentMenuMember,
        payment_data: paymentData,
      }).unwrap();

      setPaymentMenuAnchor(null);
      setPaymentMenuMember(null);
      refetchMembers();
    } catch (error: any) {
      const errorMsg = error?.data?.detail || "Failed to update payment status";
      setErrorMessage(errorMsg);
    }
  };

  // Get available circles for transfer (excluding current circle)
  const availableCircles = circles.filter((c) => c.id !== circle.id && c.is_active);

  // Render loading state
  if (membersLoading) {
    return (
      <Box data-testid="loading-members">
        <Stack spacing={2}>
          <Skeleton variant="rectangular" height={60} />
          <Skeleton variant="rectangular" height={60} />
          <Skeleton variant="rectangular" height={60} />
        </Stack>
      </Box>
    );
  }

  // Render error state
  if (membersError) {
    return <Alert severity="error">Error loading members. Please try again.</Alert>;
  }

  // Render empty state
  if (!members || members.members.length === 0) {
    return (
      <Box>
        <Typography variant="h6" gutterBottom>
          Member Management
        </Typography>
        <Alert severity="info">
          No members in this circle yet. Add some members to get started.
        </Alert>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Member Management
      </Typography>

      {errorMessage && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setErrorMessage("")}>
          {errorMessage}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Current Members Section */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Current Members
              </Typography>
              <List>
                {members.members.map((member, index) => (
                  <ListItem key={member.user_id} divider={index < members.members.length - 1}>
                    <ListItemAvatar>
                      <Avatar>
                        <PeopleIcon />
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={`User ${member.user_id}`}
                      secondary={
                        <>
                          <Chip
                            label={member.payment_status}
                            size="small"
                            color={getPaymentStatusColor(member.payment_status)}
                            variant="outlined"
                            sx={{ mr: 1 }}
                          />
                          <Typography variant="caption" component="span">
                            Joined {format(parseISO(member.joined_at), "MMM d, yyyy")}
                          </Typography>
                        </>
                      }
                    />
                    <ListItemSecondaryAction>
                      <Stack direction="row" spacing={1}>
                        <Tooltip title="Update payment status">
                          <IconButton
                            size="small"
                            onClick={(e) => handlePaymentStatusClick(e, member.user_id)}
                            aria-label="update payment status"
                          >
                            <PaymentIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Transfer member">
                          <IconButton
                            size="small"
                            onClick={() => handleTransferMember(member.user_id)}
                            aria-label="transfer member"
                          >
                            <TransferIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Remove member">
                          <IconButton
                            size="small"
                            onClick={() => handleRemoveMember(member.user_id)}
                            aria-label="remove member"
                            color="error"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </Stack>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Add Member Section */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Add New Member
              </Typography>
              <Stack spacing={2}>
                <TextField
                  label="User ID"
                  type="number"
                  value={addMemberForm.user_id}
                  onChange={(e) => setAddMemberForm({ ...addMemberForm, user_id: e.target.value })}
                  error={!!addMemberErrors.user_id}
                  helperText={addMemberErrors.user_id}
                  fullWidth
                  size="small"
                />
                <FormControl fullWidth size="small">
                  <InputLabel>Payment Status</InputLabel>
                  <Select
                    value={addMemberForm.payment_status}
                    label="Payment Status"
                    onChange={(e) =>
                      setAddMemberForm({ ...addMemberForm, payment_status: e.target.value })
                    }
                  >
                    <MenuItem value="pending">pending</MenuItem>
                    <MenuItem value="current">current</MenuItem>
                    <MenuItem value="overdue">overdue</MenuItem>
                    <MenuItem value="paused">paused</MenuItem>
                  </Select>
                </FormControl>
              </Stack>
            </CardContent>
            <CardActions>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={handleAddMember}
                disabled={addingMember}
                fullWidth
              >
                Add Member
              </Button>
            </CardActions>
          </Card>

          {/* Member Actions Info */}
          <Card sx={{ mt: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Member Actions
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Use the action buttons next to each member to:
              </Typography>
              <Box component="ul" sx={{ mt: 1, pl: 2 }}>
                <Typography component="li" variant="body2">
                  Update payment status
                </Typography>
                <Typography component="li" variant="body2">
                  Transfer to another circle
                </Typography>
                <Typography component="li" variant="body2">
                  Remove from circle
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Remove Member Confirmation Dialog */}
      <Dialog open={removeDialogOpen} onClose={() => setRemoveDialogOpen(false)}>
        <DialogTitle>Confirm Member Removal</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to remove User {memberToRemove} from this circle?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRemoveDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={confirmRemoveMember}
            color="error"
            disabled={removingMember}
            variant="contained"
          >
            Confirm
          </Button>
        </DialogActions>
      </Dialog>

      {/* Transfer Member Dialog */}
      <Dialog
        open={transferDialogOpen}
        onClose={() => setTransferDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Transfer Member</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Transfer User {memberToTransfer} to another circle.
            </Typography>
            <FormControl fullWidth error={!!transferErrors.target_circle_id}>
              <InputLabel>Target Circle</InputLabel>
              <Select
                value={transferForm.target_circle_id}
                label="Target Circle"
                onChange={(e) =>
                  setTransferForm({ ...transferForm, target_circle_id: e.target.value })
                }
              >
                {availableCircles.map((c) => (
                  <MenuItem key={c.id} value={c.id.toString()}>
                    {c.name}
                  </MenuItem>
                ))}
              </Select>
              {transferErrors.target_circle_id && (
                <FormHelperText>{transferErrors.target_circle_id}</FormHelperText>
              )}
            </FormControl>
            <TextField
              label="Reason (optional)"
              multiline
              rows={3}
              value={transferForm.reason}
              onChange={(e) => setTransferForm({ ...transferForm, reason: e.target.value })}
              placeholder="Reason for transfer..."
              fullWidth
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTransferDialogOpen(false)}>Cancel</Button>
          <Button onClick={confirmTransferMember} variant="contained" disabled={transferringMember}>
            Transfer
          </Button>
        </DialogActions>
      </Dialog>

      {/* Payment Status Menu */}
      <Menu
        anchorEl={paymentMenuAnchor}
        open={Boolean(paymentMenuAnchor)}
        onClose={() => setPaymentMenuAnchor(null)}
      >
        <MenuItem onClick={() => handlePaymentStatusUpdate("pending")}>pending</MenuItem>
        <MenuItem onClick={() => handlePaymentStatusUpdate("current")}>current</MenuItem>
        <MenuItem onClick={() => handlePaymentStatusUpdate("overdue")}>overdue</MenuItem>
        <MenuItem onClick={() => handlePaymentStatusUpdate("paused")}>paused</MenuItem>
      </Menu>
    </Box>
  );
};

export default MemberManagementInterface;
