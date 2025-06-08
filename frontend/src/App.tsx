import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import { Provider } from "react-redux";
import { theme } from "./theme";
import { store } from "./store";
import { AppLayout } from "./components/layout";
import Home from "./pages/Home";
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
            </Routes>
          </AppLayout>
        </Router>
      </ThemeProvider>
    </Provider>
  );
}

export default App;
