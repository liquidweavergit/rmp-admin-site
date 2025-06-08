import React, { useState } from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemText,
  Box,
  useTheme,
  useMediaQuery,
  Container,
} from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import HomeIcon from "@mui/icons-material/Home";
import GroupIcon from "@mui/icons-material/Group";
import EventIcon from "@mui/icons-material/Event";
import { Link, useLocation } from "react-router-dom";

interface AppLayoutProps {
  children: React.ReactNode;
}

const navigationItems = [
  { text: "Home", icon: <HomeIcon />, path: "/" },
  { text: "Circles", icon: <GroupIcon />, path: "/circles" },
  { text: "Events", icon: <EventIcon />, path: "/events" },
];

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));
  const location = useLocation();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const drawer = (
    <Box data-testid="mobile-drawer" sx={{ width: 250 }}>
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          Menu
        </Typography>
      </Toolbar>
      <List>
        {navigationItems.map((item) => (
          <ListItem
            key={item.text}
            component={Link}
            to={item.path}
            onClick={() => setMobileOpen(false)}
            sx={{
              color: "inherit",
              textDecoration: "none",
              backgroundColor: location.pathname === item.path ? "action.selected" : "transparent",
            }}
          >
            <Box sx={{ mr: 2 }}>{item.icon}</Box>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
    </Box>
  );

  const desktopNavigation = (
    <Box data-testid="desktop-navigation" sx={{ display: { xs: "none", md: "flex" }, ml: "auto" }}>
      {navigationItems.map((item) => (
        <IconButton
          key={item.text}
          component={Link}
          to={item.path}
          color="inherit"
          sx={{
            mx: 1,
            backgroundColor: location.pathname === item.path ? "action.selected" : "transparent",
          }}
        >
          {item.icon}
          <Typography variant="body2" sx={{ ml: 0.5, display: { xs: "none", lg: "block" } }}>
            {item.text}
          </Typography>
        </IconButton>
      ))}
    </Box>
  );

  return (
    <Box
      data-testid="app-layout"
      sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}
    >
      <AppBar
        data-testid="app-header"
        position="fixed"
        sx={{
          zIndex: theme.zIndex.drawer + 1,
          backgroundColor: theme.palette.primary.main,
        }}
      >
        <Toolbar>
          {isMobile && (
            <IconButton
              data-testid="mobile-menu-button"
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
          )}
          <Typography
            data-testid="app-title"
            variant="h6"
            noWrap
            component="div"
            sx={{ flexGrow: isMobile ? 1 : 0 }}
          >
            Men's Circle Platform
          </Typography>
          {!isMobile && desktopNavigation}
        </Toolbar>
      </AppBar>

      {isMobile && (
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile
          }}
          sx={{
            display: { xs: "block", md: "none" },
            "& .MuiDrawer-paper": { boxSizing: "border-box", width: 250 },
          }}
        >
          {drawer}
        </Drawer>
      )}

      <Box
        component="main"
        data-testid="main-content"
        sx={{
          flexGrow: 1,
          p: 3,
          mt: { xs: 8, sm: 9 }, // Account for fixed header
          backgroundColor: theme.palette.background.default,
        }}
      >
        <Container maxWidth="xl">{children}</Container>
      </Box>
    </Box>
  );
};

export default AppLayout;
