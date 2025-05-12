import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

const Header = () => {
  const menuItems = [
    { text: 'Home', path: '/' },
    { text: 'Configuration', path: '/config' },
    { text: 'Message Simulator', path: '/simulator' }
  ];

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          ICMP Events API Admin
        </Typography>
        <Box>
          {menuItems.map((item, index) => (
            <Button 
              key={index} 
              color="inherit" 
              component={RouterLink} 
              to={item.path}
              sx={{ mx: 1 }}
            >
              {item.text}
            </Button>
          ))}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;