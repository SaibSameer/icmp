// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Container, CssBaseline, ThemeProvider, createTheme, Box } from '@mui/material';
import Login from './components/Login';
import BusinessDetailsView from './components/BusinessDetailsView/BusinessDetailsView.jsx';
import StageManager from './components/StageManager';
import TemplateEditor from './components/TemplateEditor';
import TemplateManagement from './components/TemplateManagement';
import MessagePortal from './components/MessagePortal';
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';
import Header from './components/Header';
import Footer from './components/Footer';
import Home from './components/Home';
import StageViewPage from './pages/StageViewPage';
import MessageDebugPage from './pages/MessageDebugPage';
import { UI_CONFIG } from './config';
import { AuthProvider, useAuth } from './contexts/AuthContext';
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
  const { isAuthenticated, userId, businessId, businessApiKey, setUserId, setBusinessId, setBusinessApiKey, setIsAuthenticated } = useAuth();
  const [snackbar, setSnackbar] = React.useState({ open: false, message: '', severity: 'success' });

  const handleSnackbarOpen = (message, severity = 'success') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleSnackbarClose = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Header />
      <Container component="main" sx={{ flexGrow: 1, py: 3 }}>
        <Routes>
          <Route 
            path="/" 
            element={
              isAuthenticated ? (
                <Navigate to="/business" replace />
              ) : (
                <Navigate to="/login" replace />
              )
            } 
          />
          <Route 
            path="/messages" 
            element={
              isAuthenticated ? <MessagePortal /> : <Navigate to="/login" replace />
            } 
          />
          <Route 
            path="/stages" 
            element={
              isAuthenticated ? <StageManager /> : <Navigate to="/login" replace />
            } 
          />
          <Route 
            path="/stages/:stageId" 
            element={
              isAuthenticated ? <StageViewPage /> : <Navigate to="/login" replace />
            } 
          />
          <Route 
            path="/stage-management/business_id=:businessId/agent_id=:agentId" 
            element={
              isAuthenticated ? <StageManager /> : <Navigate to="/login" replace />
            } 
          />
          <Route 
            path="/debug/conversation/:conversationId" 
            element={
              isAuthenticated ? <MessageDebugPage /> : <Navigate to="/login" replace />
            } 
          />
          <Route 
            path="/login" 
            element={
              isAuthenticated ? (
                <Navigate to="/business" replace />
              ) : (
                <Login 
                  userId={userId}
                  setUserId={setUserId}
                  businessId={businessId}
                  setBusinessId={setBusinessId}
                  businessApiKey={businessApiKey}
                  setBusinessApiKey={setBusinessApiKey}
                  setIsAuthenticated={setIsAuthenticated}
                  handleSnackbarOpen={handleSnackbarOpen}
                />
              )
            } 
          />
          <Route 
            path="/business" 
            element={
              isAuthenticated ? (
                <BusinessDetailsView />
              ) : (
                <Navigate to="/login" replace />
              )
            } 
          />
          <Route 
            path="/templates" 
            element={
              isAuthenticated ? (
                <TemplateManagement />
              ) : (
                <Navigate to="/login" replace />
              )
            } 
          />
          <Route 
            path="/template-editor/:templateId" 
            element={
              isAuthenticated ? (
                <TemplateEditor />
              ) : (
                <Navigate to="/login" replace />
              )
            } 
          />
          <Route 
            path="/template-editor/new" 
            element={
              isAuthenticated ? (
                <TemplateEditor />
              ) : (
                <Navigate to="/login" replace />
              )
            } 
          />
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
  );
}

function App() {
  return (
    <Router>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AuthProvider>
          <AppContent />
        </AuthProvider>
      </ThemeProvider>
    </Router>
  );
}

export default App;