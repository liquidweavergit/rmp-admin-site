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
  LinearProgress,
  IconButton,
  Menu,
  MenuItem,
  Alert,
  Skeleton,
  Tabs,
  Tab,
  Badge,
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
} from "@mui/material";
import {
  Group as GroupIcon,
  Event as EventIcon,
  Add as AddIcon,
  MoreVert as MoreVertIcon,
  Schedule as ScheduleIcon,
  Payment as PaymentIcon,
  LocationOn as LocationIcon,
  People as PeopleIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  AccessTime as AccessTimeIcon,
} from "@mui/icons-material";
import { format, parseISO, isAfter, isBefore, addDays } from "date-fns";

import {
  useGetCirclesQuery,
  useGetCircleMembersQuery,
  useGetMeetingsQuery,
  useUpdateCircleMutation,
  useAddCircleMemberMutation,
  useRemoveCircleMemberMutation,
  useCreateMeetingMutation,
  useStartMeetingMutation,
  useEndMeetingMutation,
  CircleResponse,
  CircleMemberListResponse,
  MeetingListResponse,
} from "../../store";
import MemberManagementInterface from "./MemberManagementInterface";

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`circle-tabpanel-${index}`}
      aria-labelledby={`circle-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const CircleDashboard: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [selectedCircle, setSelectedCircle] = useState<CircleResponse | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  // API hooks
  const {
    data: circles = [],
    isLoading: circlesLoading,
    error: circlesError,
  } = useGetCirclesQuery();

  const { data: members, isLoading: membersLoading } = useGetCircleMembersQuery(
    selectedCircle?.id || 0,
    {
      skip: !selectedCircle,
    },
  );

  const { data: meetings, isLoading: meetingsLoading } = useGetMeetingsQuery(
    selectedCircle ? { circle_id: selectedCircle.id, per_page: 10 } : undefined,
    { skip: !selectedCircle },
  );

  const [updateCircle] = useUpdateCircleMutation();
  const [createMeeting] = useCreateMeetingMutation();
  const [startMeeting] = useStartMeetingMutation();
  const [endMeeting] = useEndMeetingMutation();

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleCircleSelect = (circle: CircleResponse) => {
    setSelectedCircle(circle);
    setTabValue(1); // Switch to detail view
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

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

  const getCapacityPercentage = (current: number, max: number) => {
    return (current / max) * 100;
  };

  const getNextMeeting = (meetings: MeetingListResponse) => {
    if (!meetings?.meetings) return null;
    const now = new Date();
    const upcomingMeetings = meetings.meetings
      .filter((meeting) => isAfter(parseISO(meeting.scheduled_date), now))
      .sort((a, b) => parseISO(a.scheduled_date).getTime() - parseISO(b.scheduled_date).getTime());
    return upcomingMeetings[0] || null;
  };

  const getRecentActivity = (meetings: MeetingListResponse) => {
    if (!meetings?.meetings) return [];
    const now = new Date();
    const lastWeek = addDays(now, -7);
    return meetings.meetings
      .filter(
        (meeting) =>
          isAfter(parseISO(meeting.created_at), lastWeek) ||
          (meeting.started_at && isAfter(parseISO(meeting.started_at), lastWeek)),
      )
      .sort((a, b) => parseISO(b.created_at).getTime() - parseISO(a.created_at).getTime())
      .slice(0, 5);
  };

  // Overview Tab Content
  const renderOverview = () => (
    <Grid container spacing={3}>
      {/* Summary Stats */}
      <Grid item xs={12}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Card elevation={2}>
              <CardContent>
                <Box display="flex" alignItems="center" gap={2}>
                  <Avatar sx={{ bgcolor: "primary.main" }}>
                    <GroupIcon />
                  </Avatar>
                  <Box>
                    <Typography variant="h4" fontWeight="bold">
                      {circles.length}
                    </Typography>
                    <Typography color="text.secondary">Total Circles</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card elevation={2}>
              <CardContent>
                <Box display="flex" alignItems="center" gap={2}>
                  <Avatar sx={{ bgcolor: "success.main" }}>
                    <PeopleIcon />
                  </Avatar>
                  <Box>
                    <Typography variant="h4" fontWeight="bold">
                      {circles.reduce((sum, circle) => sum + circle.current_member_count, 0)}
                    </Typography>
                    <Typography color="text.secondary">Total Members</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card elevation={2}>
              <CardContent>
                <Box display="flex" alignItems="center" gap={2}>
                  <Avatar sx={{ bgcolor: "warning.main" }}>
                    <EventIcon />
                  </Avatar>
                  <Box>
                    <Typography variant="h4" fontWeight="bold">
                      {meetings?.meetings?.filter((m) => m.status === "scheduled").length || 0}
                    </Typography>
                    <Typography color="text.secondary">Upcoming Meetings</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card elevation={2}>
              <CardContent>
                <Box display="flex" alignItems="center" gap={2}>
                  <Avatar sx={{ bgcolor: "info.main" }}>
                    <TrendingUpIcon />
                  </Avatar>
                  <Box>
                    <Typography variant="h4" fontWeight="bold">
                      {meetings?.meetings
                        ? Math.round(
                            meetings.meetings.reduce(
                              (sum, m) => sum + m.attendance_summary.attendance_rate,
                              0,
                            ) / meetings.meetings.length,
                          )
                        : 0}
                      %
                    </Typography>
                    <Typography color="text.secondary">Avg Attendance</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Grid>

      {/* My Circles */}
      <Grid item xs={12} lg={8}>
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">My Circles</Typography>
              <Button variant="contained" startIcon={<AddIcon />} size="small">
                Create Circle
              </Button>
            </Box>

            {circlesLoading ? (
              <Stack spacing={2}>
                {[1, 2, 3].map((i) => (
                  <Skeleton key={i} variant="rectangular" height={100} />
                ))}
              </Stack>
            ) : circlesError ? (
              <Alert severity="error">Failed to load circles</Alert>
            ) : circles.length === 0 ? (
              <Alert severity="info">
                No circles found. Create your first circle to get started!
              </Alert>
            ) : (
              <List>
                {circles.map((circle, index) => (
                  <div key={circle.id}>
                    <ListItem
                      button
                      onClick={() => handleCircleSelect(circle)}
                      sx={{ borderRadius: 1, mb: 1 }}
                    >
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: getStatusColor(circle.status) + ".main" }}>
                          <GroupIcon />
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={
                          <Box display="flex" alignItems="center" gap={1}>
                            <Typography variant="subtitle1" fontWeight="medium">
                              {circle.name}
                            </Typography>
                            <Chip
                              label={circle.status}
                              size="small"
                              color={getStatusColor(circle.status)}
                              variant="outlined"
                            />
                          </Box>
                        }
                        secondary={
                          <Stack spacing={0.5}>
                            <Typography variant="body2" color="text.secondary">
                              {circle.description || "No description"}
                            </Typography>
                            <Box display="flex" alignItems="center" gap={2} flexWrap="wrap">
                              <Box display="flex" alignItems="center" gap={0.5}>
                                <PeopleIcon fontSize="small" color="action" />
                                <Typography variant="caption">
                                  {circle.current_member_count}/{circle.capacity_max} members
                                </Typography>
                              </Box>
                              {circle.location_name && (
                                <Box display="flex" alignItems="center" gap={0.5}>
                                  <LocationIcon fontSize="small" color="action" />
                                  <Typography variant="caption">{circle.location_name}</Typography>
                                </Box>
                              )}
                            </Box>
                            <LinearProgress
                              variant="determinate"
                              value={getCapacityPercentage(
                                circle.current_member_count,
                                circle.capacity_max,
                              )}
                              sx={{ height: 4, borderRadius: 2 }}
                            />
                          </Stack>
                        }
                      />
                      <ListItemSecondaryAction>
                        <IconButton onClick={handleMenuClick}>
                          <MoreVertIcon />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                    {index < circles.length - 1 && <Divider />}
                  </div>
                ))}
              </List>
            )}
          </CardContent>
        </Card>
      </Grid>

      {/* Quick Actions & Upcoming */}
      <Grid item xs={12} lg={4}>
        <Stack spacing={3}>
          {/* Next Meeting */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Next Meeting
              </Typography>
              {meetingsLoading ? (
                <Skeleton variant="rectangular" height={80} data-testid="skeleton" />
              ) : meetings && getNextMeeting(meetings) ? (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    {getNextMeeting(meetings)?.title}
                  </Typography>
                  <Box display="flex" alignItems="center" gap={0.5} mb={1}>
                    <ScheduleIcon fontSize="small" color="action" />
                    <Typography variant="body2">
                      {getNextMeeting(meetings) &&
                        format(
                          parseISO(getNextMeeting(meetings)!.scheduled_date),
                          "MMM d, yyyy h:mm a",
                        )}
                    </Typography>
                  </Box>
                  <Button variant="outlined" size="small" fullWidth>
                    View Details
                  </Button>
                </Box>
              ) : (
                <Alert severity="info">No upcoming meetings</Alert>
              )}
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Stack spacing={1}>
                <Button variant="outlined" startIcon={<AddIcon />} fullWidth>
                  Create Circle
                </Button>
                <Button variant="outlined" startIcon={<EventIcon />} fullWidth>
                  Schedule Meeting
                </Button>
                <Button variant="outlined" startIcon={<PeopleIcon />} fullWidth>
                  Manage Members
                </Button>
              </Stack>
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Activity
              </Typography>
              {meetingsLoading ? (
                <Stack spacing={1}>
                  {[1, 2, 3].map((i) => (
                    <Skeleton key={i} variant="text" height={20} data-testid="skeleton" />
                  ))}
                </Stack>
              ) : meetings && getRecentActivity(meetings).length > 0 ? (
                <List dense>
                  {getRecentActivity(meetings).map((meeting) => (
                    <ListItem key={meeting.id} disablePadding>
                      <ListItemText
                        primary={meeting.title}
                        secondary={`${meeting.status} • ${format(parseISO(meeting.created_at), "MMM d")}`}
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No recent activity
                </Typography>
              )}
            </CardContent>
          </Card>
        </Stack>
      </Grid>
    </Grid>
  );

  // Circle Detail Tab Content
  const renderCircleDetail = () => {
    if (!selectedCircle) {
      return <Alert severity="info">Select a circle from the overview to view details</Alert>;
    }

    return (
      <Grid container spacing={3}>
        {/* Circle Header */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                <Box>
                  <Typography variant="h5" gutterBottom>
                    {selectedCircle.name}
                  </Typography>
                  <Typography variant="body1" color="text.secondary" paragraph>
                    {selectedCircle.description || "No description available"}
                  </Typography>
                </Box>
                <Chip
                  label={selectedCircle.status}
                  color={getStatusColor(selectedCircle.status)}
                  variant="outlined"
                />
              </Box>

              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="primary.main" fontWeight="bold">
                      {selectedCircle.current_member_count}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      of {selectedCircle.capacity_max} members
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={getCapacityPercentage(
                        selectedCircle.current_member_count,
                        selectedCircle.capacity_max,
                      )}
                      sx={{ mt: 1, height: 6, borderRadius: 3 }}
                    />
                  </Box>
                </Grid>

                {selectedCircle.location_name && (
                  <Grid item xs={12} sm={6} md={3}>
                    <Box textAlign="center">
                      <LocationIcon color="action" sx={{ fontSize: 40, mb: 1 }} />
                      <Typography variant="body2" fontWeight="medium">
                        {selectedCircle.location_name}
                      </Typography>
                      {selectedCircle.location_address && (
                        <Typography variant="caption" color="text.secondary" display="block">
                          {selectedCircle.location_address}
                        </Typography>
                      )}
                    </Box>
                  </Grid>
                )}

                {selectedCircle.meeting_schedule && (
                  <Grid item xs={12} sm={6} md={3}>
                    <Box textAlign="center">
                      <ScheduleIcon color="action" sx={{ fontSize: 40, mb: 1 }} />
                      <Typography variant="body2" fontWeight="medium">
                        {selectedCircle.meeting_schedule.day || "Schedule TBD"}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" display="block">
                        {selectedCircle.meeting_schedule.time || ""}
                      </Typography>
                    </Box>
                  </Grid>
                )}
              </Grid>
            </CardContent>
            <CardActions>
              <Button size="small">Edit Circle</Button>
              <Button size="small">Add Member</Button>
              <Button size="small">Schedule Meeting</Button>
            </CardActions>
          </Card>
        </Grid>

        {/* Members & Meetings */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: "100%" }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Circle Members
              </Typography>
              {membersLoading ? (
                <Stack spacing={1}>
                  {[1, 2, 3].map((i) => (
                    <Skeleton key={i} variant="rectangular" height={60} data-testid="skeleton" />
                  ))}
                </Stack>
              ) : members && members.members.length > 0 ? (
                <List>
                  {members.members.map((member) => (
                    <ListItem key={member.user_id} divider>
                      <ListItemAvatar>
                        <Avatar>
                          <PeopleIcon />
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={`User ${member.user_id}`}
                        secondary={
                          <Box display="flex" alignItems="center" gap={1}>
                            <Chip
                              label={member.payment_status}
                              size="small"
                              color={getPaymentStatusColor(member.payment_status)}
                              variant="outlined"
                            />
                            <Typography variant="caption">
                              Joined {format(parseISO(member.joined_at), "MMM d, yyyy")}
                            </Typography>
                          </Box>
                        }
                      />
                      <ListItemSecondaryAction>
                        <IconButton size="small">
                          <MoreVertIcon />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Alert severity="info">No members found</Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card sx={{ height: "100%" }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">Recent Meetings</Typography>
                <Button size="small" startIcon={<AddIcon />}>
                  Schedule
                </Button>
              </Box>
              {meetingsLoading ? (
                <Stack spacing={1}>
                  {[1, 2, 3].map((i) => (
                    <Skeleton key={i} variant="rectangular" height={60} data-testid="skeleton" />
                  ))}
                </Stack>
              ) : meetings && meetings.meetings.length > 0 ? (
                <List>
                  {meetings.meetings.slice(0, 5).map((meeting) => (
                    <ListItem key={meeting.id} divider>
                      <ListItemAvatar>
                        <Avatar
                          sx={{
                            bgcolor:
                              meeting.status === "completed" ? "success.main" : "warning.main",
                          }}
                        >
                          {meeting.status === "completed" ? (
                            <CheckCircleIcon />
                          ) : (
                            <AccessTimeIcon />
                          )}
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={meeting.title}
                        secondary={
                          <Box>
                            <Typography variant="caption" display="block">
                              {format(parseISO(meeting.scheduled_date), "MMM d, yyyy h:mm a")}
                            </Typography>
                            <Box display="flex" alignItems="center" gap={1} mt={0.5}>
                              <Chip label={meeting.status} size="small" variant="outlined" />
                              <Typography variant="caption">
                                {meeting.attendance_summary.attendance_rate}% attendance
                              </Typography>
                            </Box>
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Alert severity="info">No meetings scheduled</Alert>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Circle Dashboard
      </Typography>

      <Typography variant="body1" color="text.secondary" paragraph>
        Manage your circles, track member engagement, and facilitate meaningful connections.
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="Overview" />
          <Tab
            label={
              <Badge badgeContent={selectedCircle ? 1 : 0} color="primary">
                Circle Details
              </Badge>
            }
          />
          <Tab label="Member Management" disabled={!selectedCircle} />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        {renderOverview()}
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        {renderCircleDetail()}
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        {selectedCircle ? (
          <MemberManagementInterface circle={selectedCircle} />
        ) : (
          <Alert severity="info">Select a circle to manage its members</Alert>
        )}
      </TabPanel>

      {/* Action Menu */}
      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleMenuClose}>
        <MenuItem onClick={handleMenuClose}>View Details</MenuItem>
        <MenuItem onClick={handleMenuClose}>Edit Circle</MenuItem>
        <MenuItem onClick={handleMenuClose}>Manage Members</MenuItem>
        <MenuItem onClick={handleMenuClose}>View Meetings</MenuItem>
        <Divider />
        <MenuItem onClick={handleMenuClose}>Archive Circle</MenuItem>
      </Menu>
    </Box>
  );
};

export default CircleDashboard;
