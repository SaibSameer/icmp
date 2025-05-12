// src/App.js
import React from 'react';
import { 
  createBrowserRouter,
  RouterProvider,
  createRoutesFromElements,
  Route,
  Navigate,
  Outlet
} from 'react-router-dom';
import { Container, CssBaseline, ThemeProvider, createTheme, Box } from '@mui/material';
import Configuration from './components/Configuration';
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';
import Header from './components/Header';
import Footer from './components/Footer';
import Home from './components/Home';
import BusinessDetail from './components/BusinessDetail';
import BusinessMessages from './components/BusinessMessages';
import UserMessages from './components/UserMessages';
import StagesList from './components/StagesList';
import StageEdit from './components/StageEdit';
import DefaultStageEdit from './components/DefaultStageEdit';
import TemplateForm from './components/TemplateForm';
import TemplateEdit from './components/templates/TemplateEdit';
import TemplateTestPage from './components/templates/TemplateTestPage';
import TemplateManagement from './components/templates/TemplateManagement';
import AgentSection from './components/AgentSection';
import MessageSimulator from './components/MessageSimulator/MessageSimulator';
import { UI_CONFIG } from './config';
import { BusinessProvider } from './context/BusinessContext';
import './App.css';
import MyInterface from './components/MyInterface';
import Typography from '@mui/material/Typography';

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

function Layout() {
  const [snackbar, setSnackbar] = React.useState({ open: false, message: '', severity: 'success' });

  const handleSnackbarOpen = (message, severity = 'success') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleSnackbarClose = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <BusinessProvider>
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Header />
        <Container component="main" sx={{ flexGrow: 1, py: 3 }}>
          <Outlet context={{ handleSnackbarOpen }} />
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

// Create router with future flags
const router = createBrowserRouter(
  createRoutesFromElements(
    <Route element={<Layout />}>
      <Route path="/" element={<Home />} />
      <Route path="/config" element={<Configuration />} />
      <Route path="/business/:businessId" element={<BusinessDetail />} />
      <Route path="/business/:businessId/messages" element={<BusinessMessages />} />
      <Route path="/business/:businessId/messages/:userId" element={<UserMessages />} />
      <Route path="/business/:businessId/agents" element={<AgentSection />} />
      <Route path="/business/:businessId/stages" element={<StagesList />} />
      <Route path="/business/:businessId/stages/:stageId/edit" element={<StageEdit />} />
      <Route path="/business/:businessId/default-stages/:stageId/edit" element={<DefaultStageEdit />} />
      <Route path="/business/:businessId/templates" element={<TemplateManagement />} />
      <Route path="/business/:businessId/templates/new" element={<TemplateForm />} />
      <Route path="/business/:businessId/templates/:templateId/edit" element={<TemplateEdit />} />
      <Route path="/business/:businessId/templates/test" element={<TemplateTestPage />} />
      <Route path="/simulator" element={<MessageSimulator />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Route>
  ),
  {
    future: {
      v7_startTransition: true,
      v7_relativeSplatPath: true
    }
  }
);

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <RouterProvider router={router} />
    </ThemeProvider>
  );
}

export default App;