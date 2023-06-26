import * as React from 'react';
import { styled, useTheme } from '@mui/material/styles';
import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';
import MuiAppBar, { AppBarProps as MuiAppBarProps } from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import Chip from '@mui/material/Chip';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import { SidebarItems } from '../SidebarItems/SidebarItems';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AppRoutes } from '@/AppRoutes';
import { over } from 'lodash';
import Button from '@mui/material/Button';
import { AuthContext, AuthService } from '@/services/AuthService';
import { useContext } from 'react';
import SvgPodiumLogo from './SvgPodiumLogo';

const drawerWidth = 280;
const applicationName=import.meta.env.VITE_APPLICATION_NAME as string;

const Main = styled('main', { shouldForwardProp: (prop) => prop !== 'open' })<{
  open?: boolean;
}>(({ theme, open }) => ({
  flexGrow: 1,
  transition: theme.transitions.create('margin', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  marginLeft: `-${drawerWidth}px`,
  ...(open && {
    transition: theme.transitions.create('margin', {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
    marginLeft: 0,
  }),
}));

interface AppBarProps extends MuiAppBarProps {
  open?: boolean;
}

const AppBar = styled(MuiAppBar, {
  shouldForwardProp: (prop) => prop !== 'open',
})<AppBarProps>(({ theme, open }) => ({
  transition: theme.transitions.create(['margin', 'width'], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  ...(open && {
    width: `calc(100% - ${drawerWidth}px)`,
    marginLeft: `${drawerWidth}px`,
    transition: theme.transitions.create(['margin', 'width'], {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
  }),
}));

const DrawerHeader = styled('div')(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing(0, 1),
  // necessary for content to be below app bar
  ...theme.mixins.toolbar,
  justifyContent: 'flex-end',
}));

export const MainLayout = () => {
  const theme = useTheme();
  const authContext = useContext(AuthContext)
  const [open, setOpen] = React.useState(false);

  const handleDrawerOpen = () => {
    setOpen(!open);
  };

  const handleDrawerClose = () => {
    setOpen(false);
  };

  return (
    <Router>
      <Box sx={{ display: 'flex', overflow: 'hidden' }}>
        <AppBar
          position="fixed"
          // open={open}
          sx={{
            color:'#18B4EA',
            
           backgroundColor: '#8EC5FC',
            backgroundImage: "linear-gradient(270.35deg, #FFFFFF 73.58%, #D9F5FC 104.58%)"
            ,
            '& .MuiChip-labelSmall': {
              color: 'yellow',
              }, }}>
          <Toolbar>
            <IconButton
              color="inherit"
              aria-label="open drawer"
              onClick={handleDrawerOpen}
              edge="start"
              sx={{ mr: 2, color:'#75777A' }}
            >
             {open? <ChevronLeftIcon />:  <MenuIcon />}
            </IconButton>
            
            <SvgPodiumLogo style={{ height: '36px', width: '36px', marginLeft: '10px',marginRight:'10px' }}/>
            <Typography variant="h6" noWrap component="div" sx={{fontSize:'15px',marginRight:'5px'  }}>
              Podium
            </Typography>
            <Typography variant="h6" noWrap component="div" sx={{fontSize:'16px' ,color:'#75777A',
              fontWeight:'600'}}>
              {applicationName}
            </Typography>
            <Typography variant="subtitle2" component="span">
              <Chip
                label="Beta"
                variant="outlined"
                size="small"
                style={{ borderColor: '#e5df18', color: '#e5df18', marginLeft: '5px',marginRight:'5px' }}
              />
            </Typography>
            <Divider orientation="vertical" variant="middle" flexItem sx={{ background: 'white' ,opacity:'50%'}} />
            <Divider orientation="vertical" variant="middle" flexItem sx={{ background: 'white',marginLeft: 'auto',opacity:'50%' }} />
            <Button
              sx={{ position:'flex-end', border: '1px',marginLeft:'5px'}}
              onClick={authContext.logout}
            >
              <Typography noWrap component="div" sx={{color:'#75777A',fontSize:'14px',textTransform:'capitalize',fontWeight:'600'}}>
                Logout
              </Typography>
            </Button>
          </Toolbar>
        </AppBar>

        <Drawer
          PaperProps={{ // Add PaperProps with top spacing
            sx: { marginTop: '64px' ,
                 
                  }, // Adjust the top spacing value as needed
          }}
          sx={{
          backgroundColor : '#202123 !important',
            width: drawerWidth,
            flexShrink: 0,
            overflow: 'scroll',
            
            '& .MuiDrawer-paper': {
              width: drawerWidth,
              boxSizing: 'border-box',
              backgroundColor: 'white !important',
              color: '#75777A',
            },
            '& .MuiSvgIcon-root ':{
              color:'#75777A'
            },
            '& .Mui-selected':{
              backgroundColor:'#b3ebff !important'
            },
            '& .MuiTypography-root':{
              fontSize:'15px',
              fontWeight:'550'
            }
          }}
          variant="persistent"
          anchor="left"
          open={open}
        >
        
          <Divider />
          <SidebarItems />
        </Drawer>

        <Main open={open} className="text-white bg-[#343541]" sx={{ flexGrow: 1,paddingTop:'64px',height: '100vh', width: '100vw', overflow: 'auto', display: 'flex', flexDirection: 'column' }}>
          <Routes>
            {AppRoutes.map((route, index) => (
              <Route key={index} path={route.path} element={route.component} />
            ))}
          </Routes>
        </Main>
      </Box>
    </Router>
  );
};