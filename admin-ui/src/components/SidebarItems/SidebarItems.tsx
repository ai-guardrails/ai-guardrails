import {
  Collapse,
  Divider,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
} from "@mui/material";
import DashboardIcon from "@mui/icons-material/Dashboard";
import StorageIcon from "@mui/icons-material/Storage";
import ChatBubbleOutlineOutlinedIcon from "@mui/icons-material/ChatBubbleOutlineOutlined";
import TroubleshootOutlinedIcon from "@mui/icons-material/TroubleshootOutlined";
import BlockOutlinedIcon from "@mui/icons-material/BlockOutlined";
import EnhancedEncryptionOutlinedIcon from "@mui/icons-material/EnhancedEncryptionOutlined";
import TrendingUpOutlinedIcon from "@mui/icons-material/TrendingUpOutlined";
import GavelOutlinedIcon from "@mui/icons-material/GavelOutlined";
import ContactPageOutlinedIcon from "@mui/icons-material/ContactPageOutlined";
import SmartToyOutlinedIcon from "@mui/icons-material/SmartToyOutlined";
import VoiceOverOffOutlinedIcon from "@mui/icons-material/VoiceOverOffOutlined";
import QuestionAnswerOutlinedIcon from '@mui/icons-material/QuestionAnswerOutlined';
import PsychologyOutlinedIcon from '@mui/icons-material/PsychologyOutlined';
import ReportOutlinedIcon from '@mui/icons-material/ReportOutlined';
import ResetTvOutlinedIcon from '@mui/icons-material/ResetTvOutlined';
import SummarizeOutlinedIcon from '@mui/icons-material/SummarizeOutlined';
import { useState } from "react";
import ExpandLess from "@mui/icons-material/ExpandLess";
import ExpandMore from "@mui/icons-material/ExpandMore";
import { useNavigate , useLocation} from "react-router-dom";
export const SidebarItems = () => {
  type IconType = JSX.Element;

  interface SubMenu {
    name: string;
    link: string;
    icon: IconType;
  }
  interface SidebarItem {
    name: string;
    icon: IconType;
    isExpanded: boolean;
    link?: string;
    subMenu?: SubMenu[];
  }

  const navigate = useNavigate();
  const location = useLocation();

  const handleNavigation = (link: string) => {
    navigate(link);
  };

  const initialSidebarList = [
    {
      name: "Dashboards",
      icon: <DashboardIcon/>,
      isExpanded: false,
      link: "/risk-monitoring",
      subMenu: [
        {
          name: "Risk Monitoring",
          link: "/risk-monitoring",
          icon: <EnhancedEncryptionOutlinedIcon />,
        },
        {
          name: "Usage Monitoring",
          link: "/usage-monitoring",
          icon: <TrendingUpOutlinedIcon />,
        },
      ],
    },
    {
      name: "Data Logs",
      icon: <StorageIcon />,
      isExpanded: false,
      link: "/chat-logs",
      subMenu: [
        {
          name: "Conversation Logs",
          link: "/conversation-logs",
          icon: <QuestionAnswerOutlinedIcon />,
        },
        {
          name: "Chat Logs",
          link: "/chat-logs",
          icon: <ChatBubbleOutlineOutlinedIcon  />,
        },
        {
          name: "Analysis Logs",
          link: "/analysis-logs",
          icon: <TroubleshootOutlinedIcon />,
        },
        {
          name: "Redaction Logs",
          link: "/redaction-logs",
          icon: <BlockOutlinedIcon />,
        },
      ],
    },
    {
      name: "Detection Controls",
      icon: <PsychologyOutlinedIcon />,
      isExpanded: false,
      link: "/detection-Controls",
      subMenu: [
        {
          name: "PII Entities",
          icon: <VoiceOverOffOutlinedIcon />,
          link: "/pre-defined-rules",
        },
        {
          name: "Custom Deny Lists",
          icon: <GavelOutlinedIcon />,
          link: "/custom-deny-lists",
        },
      ],
    },
    {
      name: "Monitoring",
      icon: <ResetTvOutlinedIcon />,
      isExpanded: false,
      link: "/risk-monitoring",
      subMenu: [
        {
          name: "Escalations",
          link: "/escalations",
          icon: <ReportOutlinedIcon />,
        },
      ],
    },
    {
      name: "Detection Models",
      icon: <SmartToyOutlinedIcon />,
      link: "/detection-models",
    },
    {
      name: "User Management",
      icon: <ContactPageOutlinedIcon />,
      link: "/user-management",
    },
    {
      name: "Private Documents",
      link: "/private-documents",
      icon: <SummarizeOutlinedIcon sx={{ color: "white" }}/>,
    }
  ];
  const [sidebarList, setSidebarList] = useState(initialSidebarList);

  
  const handleToggle = (index: number) => {
    setSidebarList(
      //@ts-ignore
      //@ts-nocheck
      sidebarList.map((item, i) => {
        if (i === index) {
          return { ...item, isExpanded: !item.isExpanded };
        } else {
          return item;
        }
      })
    );
  };
  return (
    <List>
      {sidebarList.map((item, index) =>
        item.subMenu && item.subMenu.length > 0 ? (
          <>
            <ListItemButton onClick={() => handleToggle(index)}>
              <ListItemIcon sx={{ minWidth: 35 }}>{item.icon}</ListItemIcon>
              <ListItemText primary={item.name} />
              {item.isExpanded ? <ExpandLess /> : <ExpandMore />}
            </ListItemButton>
            <Collapse in={item.isExpanded} timeout="auto" unmountOnExit>
            <Divider className='bg-white' />
              <List component="div" disablePadding>
                {item.subMenu.map((subItem) => (
                  // on click navigate to subItem.link
                 <ListItem key={subItem.name} disablePadding className="ml-4"  selected={location.pathname === subItem.link}>
                 <ListItemButton onClick={() => handleNavigation(subItem.link)}>
                   <ListItemIcon sx={{ minWidth: 35 }}>{subItem.icon}</ListItemIcon>
                   <ListItemText primary={subItem.name} />
                 </ListItemButton>
               </ListItem>
                ))}
              </List>
            </Collapse>
          </>
        ) : (
          <ListItem key={item.name} disablePadding selected={location.pathname === item.link}>
            <ListItemButton onClick={() => handleNavigation(item.link)}>
              <ListItemIcon sx={{ minWidth: 35 }}>{item.icon}</ListItemIcon>
              <ListItemText primary={item.name} />
            </ListItemButton>
          </ListItem>
        )
      )}
    </List>
  );
};
