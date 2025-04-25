import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

const Header = () => {
  const menuItems = [
    { text: 'Home', path: '/' },
    { text: 'Business', path: '/business' },
    { text: 'Templates', path: '/templates' },
    { text: 'Stages', path: '/stages' }
  ];

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          ICMP Events API
        </Typography>
        <Box>
          {menuItems.map((item, index) => (
            <Button key={index} color="inherit" component={RouterLink} to={item.path}>
              {item.text}
            </Button>
          ))}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;