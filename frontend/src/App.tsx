import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import { Provider } from "react-redux";
import { theme } from "./theme";
import { store } from "./store";
import { AppLayout } from "./components/layout";
import { ProtectedRoute } from "./components/auth";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import AdminPanel from "./pages/AdminPanel";
import FacilitatorPanel from "./pages/FacilitatorPanel";
import "./App.css";

function App() {
  return (
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <AppLayout>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />

              {/* Protected Routes */}
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/facilitator"
                element={
                  <ProtectedRoute requiredRole="Facilitator" showUnauthorizedMessage={true}>
                    <FacilitatorPanel />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/admin"
                element={
                  <ProtectedRoute requiredRole="Admin" showUnauthorizedMessage={true}>
                    <AdminPanel />
                  </ProtectedRoute>
                }
              />

              {/* Example of permission-based protection */}
              <Route
                path="/admin/users"
                element={
                  <ProtectedRoute
                    requiredPermissions={["users:manage", "users:create"]}
                    requireAllPermissions={false}
                    showUnauthorizedMessage={true}
                  >
                    <AdminPanel />
                  </ProtectedRoute>
                }
              />

              {/* Example of minimum role level protection */}
              <Route
                path="/management"
                element={
                  <ProtectedRoute minimumRole="Manager" showUnauthorizedMessage={true}>
                    <Dashboard />
                  </ProtectedRoute>
                }
              />
            </Routes>
          </AppLayout>
        </Router>
      </ThemeProvider>
    </Provider>
  );
}

export default App;
