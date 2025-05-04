// src/App.js
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, Navigate, useLocation } from 'react-router-dom';
import { Container, CssBaseline, ThemeProvider, createTheme, Box } from '@mui/material';
import Configuration from './components/Configuration';
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';
import Header from './components/Header';
import Footer from './components/Footer';
import Home from './components/Home';
import BusinessDetail from './components/BusinessDetail';
import BusinessMessages from './components/BusinessMessages';
import StagesList from './components/StagesList';
import StageEdit from './components/StageEdit';
import DefaultStageEdit from './components/DefaultStageEdit';
import TemplateForm from './components/TemplateForm';
import TemplateEdit from './components/TemplateEdit';
import AgentSection from './components/AgentSection';
import ConversationMessages from './components/ConversationMessages';
import BusinessInformation from './components/BusinessInformation';
import { UI_CONFIG } from './config';
import { BusinessProvider } from './context/BusinessContext';
import './App.css';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function AppContent() {
  const [snackbar, setSnackbar] = React.useState({ open: false, message: '', severity: 'success' });
  const [isAuthenticated, setIsAuthenticated] = useState(!!sessionStorage.getItem('adminApiKey'));

  const handleSnackbarOpen = (message, severity = 'success') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleSnackbarClose = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  return (
    <BusinessProvider>
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Header />
        <Container component="main" sx={{ flexGrow: 1, py: 3 }}>
          <Routes>
            <Route 
                path="/" 
                element={isAuthenticated ? <Home /> : <Navigate replace to="/config" />}
            />
            <Route 
                path="/config"
                element={<Configuration />} 
            />
            <Route 
                path="/business/:businessId"
                element={isAuthenticated ? <BusinessDetail /> : <Navigate replace to="/config" />}
            />
            <Route 
                path="/business/:businessId/information"
                element={isAuthenticated ? <BusinessInformation /> : <Navigate replace to="/config" />}
            />
            <Route 
                path="/business/:businessId/messages"
                element={isAuthenticated ? <BusinessMessages /> : <Navigate replace to="/config" />}
            />
            <Route 
                path="/business/:businessId/conversation/:conversationId/messages"
                element={isAuthenticated ? <ConversationMessages /> : <Navigate replace to="/config" />}
            />
            <Route 
                path="/business/:businessId/agents"
                element={isAuthenticated ? <AgentSection handleSnackbarOpen={handleSnackbarOpen} /> : <Navigate replace to="/config" />}
            />
            <Route 
                path="/business/:businessId/stages"
                element={isAuthenticated ? <StagesList /> : <Navigate replace to="/config" />}
            />
            <Route 
                path="/business/:businessId/stages/:stageId/edit"
                element={isAuthenticated ? <StageEdit /> : <Navigate replace to="/config" />}
            />
            <Route 
                path="/business/:businessId/default-stages/:stageId/edit"
                element={isAuthenticated ? <DefaultStageEdit /> : <Navigate replace to="/config" />}
            />
            <Route 
                path="/business/:businessId/templates/new"
                element={isAuthenticated ? <TemplateForm /> : <Navigate replace to="/config" />}
            />
            <Route 
                path="/business/:businessId/templates/:templateId/edit"
                element={isAuthenticated ? <TemplateEdit /> : <Navigate replace to="/config" />}
            />
            <Route path="*" element={<Navigate replace to={isAuthenticated ? "/" : "/config"} />} />
          </Routes>
        </Container>
        <Footer />
        <Snackbar 
          open={snackbar.open} 
          autoHideDuration={UI_CONFIG.SNACKBAR.AUTO_HIDE_DURATION} 
          onClose={handleSnackbarClose}
          anchorOrigin={UI_CONFIG.SNACKBAR.POSITION}
        >
          <Alert onClose={handleSnackbarClose} severity={snackbar.severity} sx={{ width: '100%' }}>
            {snackbar.message}
          </Alert>
        </Snackbar>
      </Box>
    </BusinessProvider>
  );
}

function App() {
  return (
    <Router>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AppContent />
      </ThemeProvider>
    </Router>
  );
}

export default App;