import React, { useState, useMemo } from "react";
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  LinearProgress,
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
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Pagination,
  CircularProgress,
} from "@mui/material";
import {
  Group as GroupIcon,
  Event as EventIcon,
  LocationOn as LocationIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
  Warning as WarningIcon,
  Cancel as CancelIcon,
  Refresh as RefreshIcon,
  FilterList as FilterListIcon,
  ExpandMore as ExpandMoreIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon,
  People as PeopleIcon,
  Payment as PaymentIcon,
} from "@mui/icons-material";
import { format, parseISO, differenceInDays, startOfMonth, endOfMonth } from "date-fns";

import {
  useGetUserCirclesQuery,
  useGetMeetingsQuery,
  useGetCircleMembershipDetailsQuery,
  useGetUserAttendanceQuery,
  CircleResponse,
  MeetingListResponse,
  CircleMembershipDetailsResponse,
  UserAttendanceResponse,
} from "../../store";

interface DateRange {
  start?: string;
  end?: string;
}

const CircleMemberView: React.FC = () => {
  const [selectedCircle, setSelectedCircle] = useState<CircleResponse | null>(null);
  const [dateRange, setDateRange] = useState<DateRange>({});
  const [showFilters, setShowFilters] = useState(false);
  const [page, setPage] = useState(1);
  const [expandedMeeting, setExpandedMeeting] = useState<number | null>(null);

  // API hooks
  const {
    data: userCircles = [],
    isLoading: circlesLoading,
    error: circlesError,
  } = useGetUserCirclesQuery();

  const { data: meetings, isLoading: meetingsLoading } = useGetMeetingsQuery(
    selectedCircle
      ? {
          circle_id: selectedCircle.id,
          page,
          per_page: 10,
          date_from: dateRange.start,
          date_to: dateRange.end,
        }
      : undefined,
    { skip: !selectedCircle },
  );

  const { data: membershipDetails, isLoading: membershipLoading } =
    useGetCircleMembershipDetailsQuery(selectedCircle?.id || 0, {
      skip: !selectedCircle,
    });

  const { data: userAttendance, isLoading: attendanceLoading } = useGetUserAttendanceQuery(
    selectedCircle?.id || 0,
    { skip: !selectedCircle },
  );

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "active":
        return "success";
      case "forming":
        return "warning";
      case "paused":
        return "default";
      case "archived":
        return "error";
      default:
        return "default";
    }
  };

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

  const getAttendanceStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "present":
        return "success";
      case "late":
        return "warning";
      case "absent":
        return "error";
      default:
        return "default";
    }
  };

  const getAttendanceIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case "present":
        return <CheckCircleIcon />;
      case "late":
        return <ScheduleIcon />;
      case "absent":
        return <CancelIcon />;
      default:
        return <WarningIcon />;
    }
  };

  const formatMeetingSchedule = (schedule: Record<string, any> | undefined) => {
    if (!schedule) return "Schedule TBD";
    const { day, time } = schedule;
    return `${day}s at ${time}`;
  };

  const handleCircleSelect = (circle: CircleResponse) => {
    setSelectedCircle(circle);
    setPage(1);
    setDateRange({});
  };

  const handleMeetingToggle = (meetingId: number) => {
    setExpandedMeeting(expandedMeeting === meetingId ? null : meetingId);
  };

  const renderCircleSelection = () => (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        My Circle Journey
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Select a circle to view your participation history
      </Typography>

      {circlesLoading && (
        <Grid container spacing={3}>
          {[1, 2, 3].map((i) => (
            <Grid item xs={12} md={6} lg={4} key={i}>
              <Skeleton variant="rectangular" height={200} />
            </Grid>
          ))}
        </Grid>
      )}

      {circlesError && (
        <Alert severity="error" sx={{ mb: 3 }}>
          Error loading your circles. Please try again.
        </Alert>
      )}

      {!circlesLoading && !circlesError && userCircles.length === 0 && (
        <Alert severity="info" sx={{ mb: 3 }}>
          You are not currently a member of any circles. Contact your facilitator to join a circle.
        </Alert>
      )}

      {!circlesLoading && userCircles.length > 0 && (
        <Grid container spacing={3} aria-label="circle selection">
          {userCircles.map((circle) => (
            <Grid item xs={12} md={6} lg={4} key={circle.id}>
              <Card
                sx={{
                  height: "100%",
                  cursor: "pointer",
                  transition: "transform 0.2s, box-shadow 0.2s",
                  "&:hover": {
                    transform: "translateY(-2px)",
                    boxShadow: 3,
                  },
                }}
                onClick={() => handleCircleSelect(circle)}
                tabIndex={0}
                onKeyPress={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    handleCircleSelect(circle);
                  }
                }}
              >
                <CardContent>
                  <Box display="flex" alignItems="center" gap={2} mb={2}>
                    <Avatar sx={{ bgcolor: "primary.main" }}>
                      <GroupIcon />
                    </Avatar>
                    <Box flex={1}>
                      <Typography variant="h6" component="h2">
                        {circle.name}
                      </Typography>
                      <Chip
                        label={circle.status}
                        color={getStatusColor(circle.status)}
                        size="small"
                      />
                    </Box>
                  </Box>

                  <Typography variant="body2" color="text.secondary" paragraph>
                    {circle.description}
                  </Typography>

                  <Box display="flex" alignItems="center" gap={1} mb={1}>
                    <LocationIcon fontSize="small" color="action" />
                    <Typography variant="body2">{circle.location_name}</Typography>
                  </Box>

                  <Box display="flex" alignItems="center" gap={1}>
                    <ScheduleIcon fontSize="small" color="action" />
                    <Typography variant="body2">
                      {formatMeetingSchedule(circle.meeting_schedule)}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );

  const renderParticipationSummary = () => {
    if (!selectedCircle || !membershipDetails) return null;

    const { membership_stats } = membershipDetails;

    return (
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Participation Summary
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Typography variant="h6" gutterBottom>
              {selectedCircle.name}
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              {selectedCircle.description}
            </Typography>
            <Box display="flex" alignItems="center" gap={1} mb={1}>
              <LocationIcon fontSize="small" color="action" />
              <Typography variant="body2">{selectedCircle.location_name}</Typography>
            </Box>
          </Grid>

          <Grid item xs={12} md={4}>
            <Stack spacing={2}>
              <Box>
                <Typography variant="h4" color="primary">
                  {membership_stats.attendance_rate}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Attendance Rate
                </Typography>
              </Box>
              <Box>
                <Chip
                  label={
                    membershipDetails.payment_status.charAt(0).toUpperCase() +
                    membershipDetails.payment_status.slice(1)
                  }
                  color={getPaymentStatusColor(membershipDetails.payment_status)}
                  icon={<PaymentIcon />}
                />
                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                  Payment Status
                </Typography>
              </Box>
            </Stack>
          </Grid>
        </Grid>

        <Divider sx={{ my: 3 }} />

        <Grid container spacing={3}>
          <Grid item xs={6} md={3}>
            <Box textAlign="center">
              <Typography variant="h4" color="success.main">
                {membership_stats.meetings_attended}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                8 Present
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6} md={3}>
            <Box textAlign="center">
              <Typography variant="h4" color="warning.main">
                {membership_stats.meetings_late}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                2 Late
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6} md={3}>
            <Box textAlign="center">
              <Typography variant="h4" color="error.main">
                {membership_stats.meetings_absent}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                2 Absent
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6} md={3}>
            <Box textAlign="center">
              <Typography variant="h4" color="info.main">
                {membership_stats.current_streak}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Current Streak: 3
              </Typography>
            </Box>
          </Grid>
        </Grid>

        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          Member since {format(parseISO(membershipDetails.joined_at), "MMM d, yyyy")}• Longest
          streak: {membership_stats.longest_streak} meetings
        </Typography>
      </Paper>
    );
  };

  const renderMeetingHistory = () => {
    if (!selectedCircle || !meetings) return null;

    return (
      <Paper sx={{ p: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h5" component="h2">
            Meeting History
          </Typography>
          <Button
            variant="outlined"
            startIcon={<FilterListIcon />}
            onClick={() => setShowFilters(!showFilters)}
          >
            Filter
          </Button>
        </Box>

        {showFilters && (
          <Box sx={{ mb: 3, p: 2, bgcolor: "grey.50", borderRadius: 1 }}>
            <Typography variant="h6" gutterBottom>
              Date Range
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <FormControl size="small" fullWidth>
                  <InputLabel>From</InputLabel>
                  <Select
                    value={dateRange.start || ""}
                    onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
                  >
                    <MenuItem value="">All dates</MenuItem>
                    <MenuItem value={format(startOfMonth(new Date()), "yyyy-MM-dd")}>
                      This month
                    </MenuItem>
                    <MenuItem
                      value={format(
                        startOfMonth(new Date(new Date().setMonth(new Date().getMonth() - 1))),
                        "yyyy-MM-dd",
                      )}
                    >
                      Last month
                    </MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={6}>
                <FormControl size="small" fullWidth>
                  <InputLabel>To</InputLabel>
                  <Select
                    value={dateRange.end || ""}
                    onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
                  >
                    <MenuItem value="">Present</MenuItem>
                    <MenuItem value={format(endOfMonth(new Date()), "yyyy-MM-dd")}>
                      End of month
                    </MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </Box>
        )}

        {meetingsLoading && (
          <Box display="flex" justifyContent="center" p={3}>
            <CircularProgress />
          </Box>
        )}

        {!meetingsLoading && meetings.meetings.length === 0 && (
          <Alert severity="info">No meetings found for the selected criteria.</Alert>
        )}

        {!meetingsLoading && meetings.meetings.length > 0 && (
          <>
            <List>
              {meetings.meetings.map((meeting, index) => {
                const attendanceRecord = userAttendance?.find((_, i) => i === index);
                const isExpanded = expandedMeeting === meeting.id;

                return (
                  <div key={meeting.id}>
                    <ListItem
                      sx={{
                        border: 1,
                        borderColor: "divider",
                        borderRadius: 1,
                        mb: 1,
                        cursor: "pointer",
                        "&:hover": { bgcolor: "action.hover" },
                      }}
                      onClick={() => handleMeetingToggle(meeting.id)}
                    >
                      <ListItemAvatar>
                        <Avatar
                          sx={{
                            bgcolor: getAttendanceStatusColor(attendanceRecord?.status || "absent"),
                          }}
                        >
                          {getAttendanceIcon(attendanceRecord?.status || "absent")}
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={meeting.title}
                        secondary={
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              {format(parseISO(meeting.scheduled_date), "MMM d, yyyy h:mm a")}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {meeting.location_name}
                            </Typography>
                          </Box>
                        }
                      />
                      <ListItemSecondaryAction>
                        <Chip
                          label={
                            attendanceRecord?.status?.charAt(0).toUpperCase() +
                              attendanceRecord?.status?.slice(1) || "Absent"
                          }
                          color={getAttendanceStatusColor(attendanceRecord?.status || "absent")}
                          size="small"
                        />
                      </ListItemSecondaryAction>
                    </ListItem>

                    {isExpanded && (
                      <Box sx={{ ml: 7, mr: 2, mb: 2, p: 2, bgcolor: "grey.50", borderRadius: 1 }}>
                        {meeting.description && (
                          <Typography variant="body2" paragraph>
                            {meeting.description}
                          </Typography>
                        )}
                        {meeting.meeting_notes && (
                          <Typography variant="body2" paragraph>
                            <strong>Meeting Notes:</strong> {meeting.meeting_notes}
                          </Typography>
                        )}
                        {attendanceRecord?.notes && (
                          <Typography variant="body2" paragraph>
                            <strong>Personal Notes:</strong> {attendanceRecord.notes}
                          </Typography>
                        )}
                        {attendanceRecord?.checked_in_at && (
                          <Typography variant="body2" color="text.secondary">
                            Checked in: {format(parseISO(attendanceRecord.checked_in_at), "h:mm a")}
                            {attendanceRecord.checked_out_at &&
                              ` • Checked out: ${format(parseISO(attendanceRecord.checked_out_at), "h:mm a")}`}
                          </Typography>
                        )}
                      </Box>
                    )}
                  </div>
                );
              })}
            </List>

            {meetings.total > meetings.per_page && (
              <Box display="flex" justifyContent="center" mt={3}>
                <Pagination
                  count={Math.ceil(meetings.total / meetings.per_page)}
                  page={page}
                  onChange={(e, newPage) => setPage(newPage)}
                  color="primary"
                />
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ ml: 2, alignSelf: "center" }}
                >
                  {(page - 1) * meetings.per_page + 1}-
                  {Math.min(page * meetings.per_page, meetings.total)} of {meetings.total}
                </Typography>
              </Box>
            )}
          </>
        )}
      </Paper>
    );
  };

  if (circlesLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress role="progressbar" />
      </Box>
    );
  }

  return (
    <Box component="main" sx={{ p: { xs: 2, md: 3 } }}>
      {!selectedCircle ? (
        renderCircleSelection()
      ) : (
        <Box>
          <Box display="flex" alignItems="center" gap={2} mb={3}>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={() => setSelectedCircle(null)}
            >
              Back to Circles
            </Button>
            <Typography variant="h4" component="h1">
              My Circle Journey
            </Typography>
          </Box>

          {renderParticipationSummary()}
          {renderMeetingHistory()}
        </Box>
      )}
    </Box>
  );
};

export default CircleMemberView;
